
var parcelas = ee.FeatureCollection('projects/resag-1/assets/Cereal_Comarca_III')


var convencional = ee.FeatureCollection(parcelas)
    .filter(ee.Filter.eq('Manejo','Convencional'));

var conservacion = ee.FeatureCollection(parcelas)
    .filter(ee.Filter.eq('Manejo','Conservacion'));
 

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
                  .select('B2','B3','B4','B5','B6','B7','B8','B8A','B11','B12');
print(dataset)                  

// Estadisticas convencional

var stats = dataset.map(function(image) {
  return convencional.map(function(f){
    var median = image.reduceRegion({reducer: ee.Reducer.median(),geometry: f.geometry(),scale: 20});
    var std = image.reduceRegion({reducer: ee.Reducer.stdDev(),geometry: f.geometry(),scale: 20});
    return f.set({
      'date': image.date().format(),
      // MEDIA
      'B2_median': median.get('B2'),'B6_median': median.get('B6'),
      'B3_median': median.get('B3'),'B7_median': median.get('B7'),
      'B4_median': median.get('B4'),'B8_median': median.get('B8'),
      'B5_median': median.get('B5'),'B8A_median': median.get('B8A'),
      'B11_median': median.get('B11'),'B12_median': median.get('B12'),
      // DESVIACION ESTANDAR
      'B2_std': std.get('B2'),'B6_std': std.get('B6'),
      'B3_std': std.get('B3'),'B7_std': std.get('B7'),
      'B4_std': std.get('B4'),'B8_std': std.get('B8'),
      'B5_std': std.get('B5'),'B8A_std': std.get('B8A'),
      'B11_std': std.get('B11'),'B12_std': std.get('B12'),
    })
  })
})
.flatten()
// MEDIA
.filter(ee.Filter.neq('B2_median', null))
.filter(ee.Filter.neq('B3_median', null)).filter(ee.Filter.neq('B4_median', null))
.filter(ee.Filter.neq('B5_median', null)).filter(ee.Filter.neq('B6_median', null))
.filter(ee.Filter.neq('B7_median', null)).filter(ee.Filter.neq('B8_median', null))
.filter(ee.Filter.neq('B8A_median', null)).filter(ee.Filter.neq('B11_median', null))
.filter(ee.Filter.neq('B12_median', null))
// DESVIACION ESTANDAR
.filter(ee.Filter.neq('B2_std', null))
.filter(ee.Filter.neq('B3_std', null)).filter(ee.Filter.neq('B4_std', null))
.filter(ee.Filter.neq('B5_std', null)).filter(ee.Filter.neq('B6_std', null))
.filter(ee.Filter.neq('B7_std', null)).filter(ee.Filter.neq('B8_std', null))
.filter(ee.Filter.neq('B8A_std', null)).filter(ee.Filter.neq('B11_std', null))
.filter(ee.Filter.neq('B12_std', null));
// Export
Export.table.toDrive({
  collection: stats,
  description: 'Comarca_III_median_bandas_S2_convencional',
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
      // MEDIA
      'B2_median': median.get('B2'),'B6_median': median.get('B6'),
      'B3_median': median.get('B3'),'B7_median': median.get('B7'),
      'B4_median': median.get('B4'),'B8_median': median.get('B8'),
      'B5_median': median.get('B5'),'B8A_median': median.get('B8A'),
      'B11_median': median.get('B11'),'B12_median': median.get('B12'),
      // DESVIACION ESTANDAR
      'B2_std': std.get('B2'),'B6_std': std.get('B6'),
      'B3_std': std.get('B3'),'B7_std': std.get('B7'),
      'B4_std': std.get('B4'),'B8_std': std.get('B8'),
      'B5_std': std.get('B5'),'B8A_std': std.get('B8A'),
      'B11_std': std.get('B11'),'B12_std': std.get('B12'),
    })
  })
})
.flatten()
// MEDIA
.filter(ee.Filter.neq('B2_median', null))
.filter(ee.Filter.neq('B3_median', null)).filter(ee.Filter.neq('B4_median', null))
.filter(ee.Filter.neq('B5_median', null)).filter(ee.Filter.neq('B6_median', null))
.filter(ee.Filter.neq('B7_median', null)).filter(ee.Filter.neq('B8_median', null))
.filter(ee.Filter.neq('B8A_median', null)).filter(ee.Filter.neq('B11_median', null))
.filter(ee.Filter.neq('B12_median', null))
// DESVIACION ESTANDAR
.filter(ee.Filter.neq('B2_std', null))
.filter(ee.Filter.neq('B3_std', null)).filter(ee.Filter.neq('B4_std', null))
.filter(ee.Filter.neq('B5_std', null)).filter(ee.Filter.neq('B6_std', null))
.filter(ee.Filter.neq('B7_std', null)).filter(ee.Filter.neq('B8_std', null))
.filter(ee.Filter.neq('B8A_std', null)).filter(ee.Filter.neq('B11_std', null))
.filter(ee.Filter.neq('B12_std', null));
// Export
Export.table.toDrive({
  collection: stats,
  description: 'Comarca_III_median_bandas_S2_conservacion',
  fileFormat: 'CSV',
  folder: 'Proyecto_ReSag'
}); 
