#!/usr/bin/env python

from cStringIO import StringIO
import glob
import gzip
import json
import os
import re
import shutil
import sys

from pake import Target, ifind, main, output, rule, target, variables, virtual


if sys.platform == 'win32':
    variables.GIT = 'C:/Program Files/Git/bin/git.exe'
    variables.GJSLINT = 'gjslint'  # FIXME
    variables.JAVA = 'C:/Program Files/Java/jre7/bin/java.exe'
    variables.JSDOC = 'jsdoc'  # FIXME
    variables.PHANTOMJS = 'phantomjs'  # FIXME
    variables.PYTHON = 'C:/Python27/python.exe'
else:
    variables.GIT = 'git'
    variables.GJSLINT = 'gjslint'
    variables.JAVA = 'java'
    variables.JSDOC = 'jsdoc'
    variables.PHANTOMJS = 'phantomjs'
    variables.PYTHON = 'python'

variables.BRANCH = output('%(GIT)s', 'rev-parse', '--abbrev-ref', 'HEAD').strip()

EXPORTS = [path
           for path in ifind('src')
           if path.endswith('.exports')
           if path != 'src/objectliterals.exports']

EXTERNAL_SRC = [
    'build/src/external/externs/types.js',
    'build/src/external/src/exports.js',
    'build/src/external/src/types.js']

EXAMPLES = [path
            for path in glob.glob('examples/*.html')
            if path != 'examples/example-list.html']

EXAMPLES_SRC = [path
                for path in ifind('examples')
                if path.endswith('.js')
                if not path.endswith('.combined.js')
                if path != 'examples/Jugl.js'
                if path != 'examples/example-list.js']

INTERNAL_SRC = [
    'build/src/internal/src/requireall.js',
    'build/src/internal/src/types.js']

SPEC = [path
        for path in ifind('test/spec')
        if path.endswith('.js')]

SRC = [path
       for path in ifind('src/ol')
       if path.endswith('.js')]

PLOVR_JAR = 'bin/plovr-eba786b34df9.jar'
PLOVR_JAR_MD5 = '20eac8ccc4578676511cf7ccbfc65100'


def report_sizes(t):
    t.info('uncompressed: %d bytes', os.stat(t.name).st_size)
    stringio = StringIO()
    gzipfile = gzip.GzipFile(t.name, 'w', 9, stringio)
    with open(t.name) as f:
        shutil.copyfileobj(f, gzipfile)
    gzipfile.close()
    t.info('  compressed: %d bytes', len(stringio.getvalue()))


virtual('all', 'build-all', 'build', 'examples')


virtual('precommit', 'lint', 'build-all', 'test', 'build', 'build-examples', 'doc')


virtual('build', 'build/ol.css', 'build/ol.js')


virtual('todo', 'fixme')


@target('build/ol.css', 'build/ol.js')
def build_ol_css(t):
    t.touch()


@target('build/ol.js', PLOVR_JAR, SRC, EXTERNAL_SRC, 'base.json', 'build/ol.json')
def build_ol_js(t):
    t.output('%(JAVA)s', '-jar', PLOVR_JAR, 'build', 'build/ol.json')
    report_sizes(t)


virtual('build-all', 'build/ol-all.js')


@target('build/ol-all.js', PLOVR_JAR, SRC, INTERNAL_SRC, 'base.json', 'build/ol-all.json')
def build_ol_all_js(t):
    t.output('%(JAVA)s', '-jar', PLOVR_JAR, 'build', 'build/ol-all.json')


@target('build/src/external/externs/types.js', 'bin/generate-exports.py', 'src/objectliterals.exports')
def build_src_external_externs_types_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py', '--externs', 'src/objectliterals.exports')


@target('build/src/external/src/exports.js', 'bin/generate-exports.py', 'src/objectliterals.exports', EXPORTS)
def build_src_external_src_exports_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py', '--exports', 'src/objectliterals.exports', EXPORTS)


@target('build/src/external/src/types.js', 'bin/generate-exports', 'src/objectliterals.exports')
def build_src_external_src_types_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py', '--typedef', 'src/objectliterals.exports')


@target('build/src/internal/src/requireall.js', SRC)
def build_src_internal_src_requireall_js(t):
    requires = set(('goog.dom',))
    for dependency in t.dependencies:
        for line in open(dependency):
            match = re.match(r'goog\.provide\(\'(.*)\'\);', line)
            if match:
                requires.add(match.group(1))
    with open(t.name, 'w') as f:
        for require in sorted(requires):
            f.write('goog.require(\'%s\');\n' % (require,))


@target('build/src/internal/src/types.js', 'bin/generate-exports.py', 'src/objectliterals.exports')
def build_src_internal_types_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py', '--typedef', 'src/objectliterals.exports')


virtual('build-examples', 'examples', (path.replace('.html', '.combined.js') for path in EXAMPLES))


virtual('examples', 'examples/example-list.js', (path.replace('.html', '.json') for path in EXAMPLES))


@target('examples/example-list.js', 'bin/exampleparser.py', EXAMPLES)
def examples_examples_list_js(t):
    t.run('%(PYTHON)s', 'bin/exampleparser.py', 'examples', 'examples')


@rule(r'\Aexamples/(?P<id>.*).json\Z')
def examples_star_json(name, match):
    def action(t):
        content = json.dumps({
            'id': match.group('id'),
            'inherits': '../base.json',
            'inputs': [
                'examples/%(id)s.js' % match.groupdict(),
                'build/src/internal/src/types.js',
            ],
        })
        with open(t.name, 'w') as f:
            f.write(content)
    dependencies = [__file__, 'base.json']
    return Target(name, action=action, dependencies=dependencies)


@rule(r'\Aexamples/(?P<id>.*).combined.js\Z')
def examples_star_combined_js(name, match):
    def action(t):
        t.output('%(JAVA)s', '-jar', PLOVR_JAR, 'build', 'examples/%(id)s.json' % match.groupdict())
        report_sizes(t)
    dependencies = [PLOVR_JAR, SRC, INTERNAL_SRC, 'base.json', 'examples/%(id)s.js' % match.groupdict(), 'examples/%(id)s.json' % match.groupdict()]
    return Target(name, action=action, dependencies=dependencies)


@target('serve', PLOVR_JAR, INTERNAL_SRC, 'examples')
def serve(t):
    t.run('%(JAVA)s', '-jar', PLOVR_JAR, 'serve', glob.glob('build/*.json'), glob.glob('examples/*.json'))


@target('serve-precommit', PLOVR_JAR, INTERNAL_SRC)
def serve_precommit(t):
    t.run('%(JAVA)s', '-jar', PLOVR_JAR, 'serve', 'build/ol-all.json')


virtual('lint', 'build/lint-src-timestamp', 'build/lint-spec-timestamp')


@target('build/lint-src-timestamp', SRC, INTERNAL_SRC, EXTERNAL_SRC, EXAMPLES_SRC)
def build_lint_src_timestamp(t):
    limited_doc_files = [path
                         for path in ifind('externs', 'build/src/external/externs')
                         if path.endswith('.js')]
    t.run('%(GJSLINT)s', '--strict', '--limited_doc_files=%s' % (','.join(limited_doc_files),), t.newer(SRC, INTERNAL_SRC, EXTERNAL_SRC, EXAMPLES_SRC))
    t.touch()


@target('build/lint-spec-timestamp', SPEC)
def build_lint_spec_timestamp(t):
    t.run('%(GJSLINT)s', t.newer(SPEC))
    t.touch()


virtual('plovr', PLOVR_JAR)


@target(PLOVR_JAR, clean=False)
def plovr_jar(t):
    t.download('https://plovr.googlecode.com/files/' + os.path.basename(PLOVR_JAR), md5=PLOVR_JAR_MD5)


@target('gh-pages', 'hostexamples', 'doc', phony=True)
def gh_pages(t):
    with t.tempdir() as tempdir:
        t.run('%(GIT)s', 'clone', '--branch', 'gh-pages', 'git@github.com:openlayers/ol3.git', tempdir)
        with t.chdir(tempdir):
            t.rm_rf('%(BRANCH)s')
        t.cp_r('build/gh-pages/%(BRANCH)s', tempdir + '/%(BRANCH)s')
        with t.chdir(tempdir):
            t.run('%(GIT)s', 'add', '--all', '%(BRANCH)s')
            t.run('%(GIT)s', 'commit', '--message', 'Updated')
            t.run('%(GIT)s', 'push', 'origin', 'gh-pages')


virtual('doc', 'build/jsdoc-%(BRANCH)s-timestamp' % vars(variables))


@target('build/jsdoc-%(BRANCH)s-timestamp' % vars(variables), SRC, ifind('doc/template'))
def jsdoc_BRANCH_timestamp(t):
    t.run('%(JSDOC)s', '-t', 'doc/template', '-r', 'src', '-d', 'build/gh-pages/%(BRANCH)s/apidoc')
    t.touch()


@target('hostexamples', 'build', 'examples', phony=True)
def hostexamples(t):
    t.makedirs('build/gh-pages/%(BRANCH)s/examples')
    t.makedirs('build/gh-pages/%(BRANCH)s/build')
    t.cp(EXAMPLES, (path.replace('.html', '.js') for path in EXAMPLES), 'examples/style.css', 'build/gh-pages/%(BRANCH)s/examples/')
    t.cp('build/loader_hosted_examples.js', 'build/gh-pages/%(BRANCH)s/examples/loader.js')
    t.cp('build/ol.js', 'build/ol.css', 'build/gh-pages/%(BRANCH)s/build/')
    t.cp('examples/example-list.html', 'build/gh-pages/%(BRANCH)s/examples/index.html')
    t.cp('examples/example-list.js', 'examples/example-list.xml', 'examples/Jugl.js', 'build/gh-pages/%(BRANCH)s/examples/')


@target('test', INTERNAL_SRC, phony=True)
def test(t):
    t.run('%(PHANTOMJS)s', 'test/phantom-jasmine/run_jasmine_test.coffee', 'test/ol.html')

@target('fixme', phony=True)
def find_fixme(t):
    regex = re.compile(".(FIXME|TODO).")
    matches = dict()
    totalcount = 0
    for filename in SRC:
        f = open(filename, 'r')
        for lineno, line in enumerate(f):
            if regex.search(line):
                if (filename not in matches):
                    matches[filename] = list()
                matches[filename].append("#" + str(lineno + 1).ljust(10) + line.strip())
                totalcount += 1
        f.close()

    for filename in matches:
        print "  ", filename, "has", len(matches[filename]), "matches:"
        for match in matches[filename]:
            print "    ", match
        print
    print "A total number of", totalcount, "TODO/FIXME was found"

if __name__ == '__main__':
    main()
