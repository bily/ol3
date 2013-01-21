goog.provide('ol.layer.SingleImageLayer');

goog.require('ol.layer.Layer');
goog.require('ol.source.SingleImageSource');



/**
 * @constructor
 * @extends {ol.layer.Layer}
 * @param {ol.layer.LayerOptions} layerOptions Layer options.
 */
ol.layer.SingleImageLayer = function(layerOptions) {
  goog.base(this, layerOptions);
};
goog.inherits(ol.layer.SingleImageLayer, ol.layer.Layer);


/**
 * @return {ol.source.SingleImageSource} Single image source.
 */
ol.layer.SingleImageLayer.prototype.getSingleImageSource = function() {
  return /** @type {ol.source.SingleImageSource} */ (this.getSource());
};
