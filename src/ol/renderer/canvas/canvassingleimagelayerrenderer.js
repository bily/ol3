goog.provide('ol.renderer.canvas.SingleImageLayer');

goog.require('goog.vec.Mat4');
goog.require('ol.Extent');
goog.require('ol.SingleImage');
goog.require('ol.layer.SingleImageLayer');
goog.require('ol.renderer.Map');
goog.require('ol.renderer.canvas.Layer');



/**
 * @constructor
 * @extends {ol.renderer.canvas.Layer}
 * @param {ol.renderer.Map} mapRenderer Map renderer.
 * @param {ol.layer.SingleImageLayer} singleImageLayer Single image layer.
 */
ol.renderer.canvas.SingleImageLayer = function(mapRenderer, singleImageLayer) {

  goog.base(this, mapRenderer, singleImageLayer);

  /**
   * @private
   * @type {?ol.SingleImage}
   */
  this.singleImage_ = null;

  /**
   * @private
   * @type {!goog.vec.Mat4.Number}
   */
  this.transform_ = goog.vec.Mat4.createNumber();

};
goog.inherits(ol.renderer.canvas.SingleImageLayer, ol.renderer.canvas.Layer);


/**
 * @inheritDoc
 */
ol.renderer.canvas.SingleImageLayer.prototype.getImage = function() {
  return this.singleImage_.image;
};


/**
 * @return {ol.layer.SingleImageLayer} Single image layer.
 */
ol.renderer.canvas.SingleImageLayer.prototype.getSingleImageLayer = function() {
  return /** @type {ol.layer.SingleImageLayer} */ (this.getLayer());
};


/**
 * @inheritDoc
 */
ol.renderer.canvas.SingleImageLayer.prototype.getTransform = function() {
  return this.transform_;
};


/**
 * @inheritDoc
 */
ol.renderer.canvas.SingleImageLayer.prototype.renderFrame =
    function(frameState, layerState) {

  var view2DState = frameState.view2DState;

  var singleImageLayer = this.getSingleImageLayer();
  var singleImageSource = singleImageLayer.getSingleImageSource();
  var singleImage = singleImageSource.getSingleImage(); // FIXME pass args

  this.singleImage_ = singleImage;

  var imageResolution = singleImage.resolution;
  var transform = this.transform_;
  goog.vec.Mat4.makeIdentity(transform);
  goog.vec.Mat4.translate(transform,
      frameState.size.width / 2, frameState.size.height / 2, 0);
  goog.vec.Mat4.rotateZ(transform, view2DState.rotation);
  goog.vec.Mat4.scale(
      transform,
      imageResolution / view2DState.resolution,
      imageResolution / view2DState.resolution,
      1);
  goog.vec.Mat4.translate(
      transform,
      (singleImage.extent.minX - view2DState.center.x) / imageResolution,
      (view2DState.center.y - singleImage.extent.maxY) / imageResolution,
      0);

};
