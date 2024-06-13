
var parcelas = ee.FeatureCollection('projects/resag-1/assets/Cereal_Comarca_III');


var convencional = ee.FeatureCollection(parcelas)
    .filter(ee.Filter.eq('Manejo','Convencional'));

var conservacion = ee.FeatureCollection(parcelas)
    .filter(ee.Filter.eq('Manejo','Conservacion'));
 
    
var addindices = function(image) {
  
  var NDSVI = image.normalizedDifference(['B11','B4']).rename('NDSVI');  
  var NDI7 = image.normalizedDifference(['B8A','B12']).rename('NDI7'); 
  var DFI = image.expression(                                               
      '100*(1-B12/B11)*(B4/B8)', {         
      'B11': image.select('B11'),
      'B12': image.select('B12'),
      'B4' : image.select('B4'),
      'B8': image.select('B8')
    }).rename('DFI'); 
  var RATIO = image.expression(                                               /// Triangle vegetation index
      'B12/B11'/*10000*/, {         
      'B11': image.select('B11'),
      'B12': image.select('B12')
    }).rename('RATIO');
  var NDTI = image.normalizedDifference(['B11','B12']).rename('NDTI'); /// normalized Diff Red Edge Index
  var STI = image.expression(                                               /// Triangle vegetation index
      'B11/B12',{         // DIVIDIDO PARA 10000 POR LA REFLECTANCIA ADICIONAL 10 PARA RANGO
      'B11': image.select('B11'),
      'B12': image.select('B12')
    }).rename('STI');
    var SINDRI = image.expression(                                               /// Triangle vegetation index
      '((B11-B12)/(B11+B12))*100',{         // DIVIDIDO PARA 10000 POR LA REFLECTANCIA ADICIONAL 10 PARA RANGO
      'B11': image.select('B11'),
      'B12': image.select('B12')
    }).rename('SINDRI');
  return image.addBands([NDSVI,NDI7,NDTI,STI,RATIO,DFI,SINDRI]);
};



// Funcion mascara de nubes con la banda SCL
function maskclouds_scl(imagen) {
  var scl = imagen.select('SCL');
  // Seleccionar las clases de vegetacion, suelo, agua y nieve
  var veg = 4;
  var soil = 5;
  var water = 6;
  var snow = 11;
  // Mascara
  var mask = scl.eq(veg).or(scl.eq(soil)).or(scl.eq(water)).or(scl.eq(snow));
  var properties = imagen.propertyNames();
  var imagen_mask = ee.Image(imagen.updateMask(mask).copyProperties(imagen,properties));
  return imagen_mask;
}


// coleccion de imagenes sentincel-2 LA2
var S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED");

var dataset = S2.filter(ee.Filter.date('2022-07-01', '2023-06-30'))
                // filtro inicialmente por nubosidad
                  //.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',10))
                  .filterBounds(parcelas)
                  .map(maskclouds_scl)
                  .map(addindices)
                  //.map(add_nirv)
                  .select('B2','B3','B4','B5','B6','B7','B8','B8A','B11','B12',
                          'NDSVI','NDI7','NDTI','STI','RATIO','DFI','SINDRI');
print(dataset)                  

// Estadisticas convencional

var stats = dataset.map(function(image) {
  return convencional.map(function(f){
    var median = image.reduceRegion({reducer: ee.Reducer.median(),geometry: f.geometry(),scale: 20});
    var std = image.reduceRegion({reducer: ee.Reducer.stdDev(),geometry: f.geometry(),scale: 20});
    return f.set({
      'date': image.date().format(),
      // MEDIA
      'NDSVI_median': median.get('NDSVI'),'NDI7_median': median.get('NDI7'),
      'NDTI_median': median.get('NDTI'),'STI_median': median.get('STI'),
      'RATIO_median': median.get('RATIO'),'DFI_median': median.get('DFI')

    });
  });
})
.flatten()
// MEDIA
.filter(ee.Filter.neq('NDSVI_median', null)).filter(ee.Filter.neq('NDI7_median', null))
.filter(ee.Filter.neq('NDTI_median', null)).filter(ee.Filter.neq('STI_median', null))
.filter(ee.Filter.neq('RATIO_median', null)).filter(ee.Filter.neq('DFI_median', null));

// Export
Export.table.toDrive({
  collection: stats,
  description: 'Comarca_III_median_indices_S2_convencional',
  fileFormat: 'CSV',
  folder: 'Proyecto_ReSag'
}); 

//Estadisticas conservacion
var stats = dataset.map(function(image) {
  return conservacion.map(function(f){
    var median = image.reduceRegion({reducer: ee.Reducer.median(),geometry: f.geometry(),scale: 20});
    var std = image.reduceRegion({reducer: ee.Reducer.stdDev(),geometry: f.geometry(),scale: 20});
    return f.set({
      'date': image.date().format(),
      'NDSVI_median': median.get('NDSVI'),'NDI7_median': median.get('NDI7'),
      'NDTI_median': median.get('NDTI'),'STI_median': median.get('STI'),
      'RATIO_median': median.get('RATIO'),'DFI_median': median.get('DFI')


    });
  });
})
.flatten()
// MEDIA
.filter(ee.Filter.neq('NDSVI_median', null)).filter(ee.Filter.neq('NDI7_median', null))
.filter(ee.Filter.neq('NDTI_median', null)).filter(ee.Filter.neq('STI_median', null))
.filter(ee.Filter.neq('RATIO_median', null)).filter(ee.Filter.neq('DFI_median', null));





// Export
Export.table.toDrive({
  collection: stats,
  description: 'Comarca_III_median_indices_S2_conservacion',
  fileFormat: 'CSV',
  folder: 'Proyecto_ReSag'
}); 



