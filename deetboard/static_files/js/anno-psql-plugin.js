/**
 * A simple storage connector plugin to the PSQL.
 *
 * Note: the plugin requires jQuery to be linked into the host page.
 *
 */
annotorious.plugin.PSQL = function(opt_config_options) {
  /** @private **/
  this._STORE_URI = opt_config_options['base_url'];

  this._MEDIA_URI = opt_config_options['media_url'];

  /** @private **/
  //this._annotations = [];

  this._expertAnnos = opt_config_options['annotations'][0]
  this._otherAnnos = opt_config_options['annotations'][1]

  this._allAnnos = this._expertAnnos.concat(this._otherAnnos)
  
  /** @private **/
  this._loadIndicators = [];

}

annotorious.plugin.PSQL.prototype.initPlugin = function(anno) {  
  var self = this;
  anno.addHandler('onAnnotationCreated', function(annotation) {
    console.log("onAnnotationCreated");
    self._create(annotation);
  });

  anno.addHandler('onAnnotationUpdated', function(annotation) {
    self._update(annotation);
  });

  anno.addHandler('onAnnotationRemoved', function(annotation) {
    self._delete(annotation);
  });

  annoList = this._allAnnos;

  self._loadAnnotations(anno, annoList);

  self._setHooks(anno);
  
}

annotorious.plugin.PSQL.prototype._setHooks = function(anno) {  
  console.log("HEY There!");
  var self = this;

  
  var allAnnos = self._allAnnos;
  var expertAnnos = self._expertAnnos;
  var otherAnnos = self._otherAnnos;
  // edit annotation lsit based on select div's value
  $( "#expert-image" ).click(function() {
    console.log(self._otherAnnos)
    anno.hideAnnotations();
  });
  var self = this;
  $( "#questions-header" ).click(function() {
    anno.showAnnotations();
  });

  $( "#allAnnos" ).click(function() {
    anno.removeAll();
    self._loadAnnotations(anno, allAnnos)
  });
  $( "#expertAnnos" ).click(function() {
    anno.removeAll();
    self._loadAnnotations(anno, expertAnnos)
  });
  $( "#otherAnnos" ).click(function() {
    anno.removeAll();
    self._loadAnnotations(anno, otherAnnos)
  });

}

annotorious.plugin.PSQL.prototype.onInitAnnotator = function(annotator) {
  var spinner = this._newLoadIndicator();
  annotator.element.appendChild(spinner);
  this._loadIndicators.push(spinner);
}

annotorious.plugin.PSQL.prototype._newLoadIndicator = function() { 
  var outerDIV = document.createElement('div');
  outerDIV.className = 'annotorious-es-plugin-load-outer';
  
  var innerDIV = document.createElement('div');
  innerDIV.className = 'annotorious-es-plugin-load-inner';
  
  outerDIV.appendChild(innerDIV);
  return outerDIV;
}

/**
 * @private
 */
annotorious.plugin.PSQL.prototype._showError = function(error) {
  // TODO proper error handling
  window.alert('ERROR');
  console.log(error);
}

/**
 * @private
 */
annotorious.plugin.PSQL.prototype._loadAnnotations = function(anno, annoList) {
  // TODO need to restrict search to the URL of the annotated
  var self = this;
  
  var annos = annoList
  console.log(annos)
  for (i = 0; i < annos.length; i++) { 
    var annotationFields = annos[i][0]["fields"]
    
    var rectGeometry = {};
    rectGeometry["x"] = annotationFields["x_val"];
    rectGeometry["y"] = annotationFields["y_val"];;
    rectGeometry["width"] = annotationFields["width"];;
    rectGeometry["height"] = annotationFields["height"];;
    
    var shape1 = {};
    shape1['geometry'] = rectGeometry;
    shape1['style'] = annotationFields["style"];;
    shape1['type'] = annotationFields["shapeType"];
    
    var shapes = [];
    shapes.push(shape1);

    annotation = {};
    annotation['src'] = this._MEDIA_URI + annotationFields["src"];;
    annotation['shapes'] = shapes;
    annotation['context'] = annotationFields["context"];;
    annotation['text'] = annotationFields["text"];;

    anno.addAnnotation(annotation);
  }
  
  
  
  /* Querying /_search for annotations
  jQuery.getJSON(this._STORE_URI + '_search?query=*:*&size=1000', function(data) {
    try {
      
      jQuery.each(data.hits.hits, function(idx, hit) {
        var annotation = hit['_source'];
        console.log(annotation);
        annotation.id = hit['_id'];
        
        if (jQuery.inArray(annotation.id, self._annotations) < 0) {
          self._annotations.push(annotation.id);
          if (!annotation.shape && annotation.shapes[0].geometry)
            anno.addAnnotation(annotation);
        }
      });
    } catch (e) {
      self._showError(e);
    }
    
    // Remove all load indicators
    jQuery.each(self._loadIndicators, function(idx, spinner) {
      jQuery(spinner).remove();
    });
  });
  */
}



/**
 * @private
 */
annotorious.plugin.PSQL.prototype._create = function(annotation) {
  var self = this;
  console.log("_create");
  console.log(this);
  console.log("Another!");
  console.log(JSON.stringify(annotation));
  jQuery.post(this._STORE_URI + 'annotation/',  JSON.stringify(annotation), function(response) {
    console.log("response");
    console.log(response);
    // TODO error handling if response status != 201 (CREATED)
    var id = response['_id'];
    annotation.id = id;
  });
}

/**
 * @private
 */
annotorious.plugin.PSQL.prototype._update = function(annotation) {
  var self = this;
  jQuery.ajax({
    url: this._STORE_URI + 'annotation/' + annotation.id,
    type: 'PUT',
    data: JSON.stringify(annotation)
  }); 
}

/**
 * @private
 */
annotorious.plugin.PSQL.prototype._delete = function(annotation) {
  jQuery.ajax({
    url: this._STORE_URI + 'annotation/' + annotation.id,
    type: 'DELETE'
  });
}