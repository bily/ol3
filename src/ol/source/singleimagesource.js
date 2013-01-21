goog.provide('ol.SingleImage');
goog.provide('ol.source.SingleImageSource');

goog.require('ol.Attribution');
goog.require('ol.Extent');
goog.require('ol.Projection');
goog.require('ol.source.Source');


/**
 * @typedef {{extent: ol.Extent,
 *            image: (HTMLCanvasElement|HTMLVideoElement|Image),
 *            resolution: number}}
 */
ol.SingleImage;


/**
 * @typedef {{attribtions: (Array.<ol.Attribution>|undefined),
 *            extent: (ol.Extent|undefined),
 *            projection: (ol.Projection|undefined)}}
 */
ol.source.SingleImageSourceOptions;



/**
 * @constructor
 * @extends {ol.source.Source}
 * @param {ol.source.SingleImageSourceOptions} singleImageSourceOptions Single
 *     image source options.
 */
ol.source.SingleImageSource = function(singleImageSourceOptions) {

  goog.base(this, {
    attribtions: singleImageSourceOptions.attribtions,
    extent: singleImageSourceOptions.extent,
    projection: singleImageSourceOptions.projection
  });

};
goog.inherits(ol.source.SingleImageSource, ol.source.Source);


/**
 * @return {ol.SingleImage} Single image.
 */
ol.source.SingleImageSource.prototype.getSingleImage = function() {
  return {
    extent: new ol.Extent(0, 0, 0, 0),
    image: new Image(),
    resolution: 0
  };
};
