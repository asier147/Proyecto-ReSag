// Load the parcels FeatureCollection
var parcelas = ee.FeatureCollection('projects/resag-1/assets/Cereal_Comarca_III');

// Filter parcels for 'Convencional' management
var convencional = ee.FeatureCollection(parcelas)
    .filter(ee.Filter.eq('Manejo','Convencional'));
// Filter parcels for 'Conservacion' management
var conservacion = ee.FeatureCollection(parcelas)
    .filter(ee.Filter.eq('Manejo','Conservacion'));
 
// Function to add vegetation indices as bands to each image    
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



// Function to mask clouds using the Scene Classification (SCL) band
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


// Load Sentinel-2 Level-2A imagery collection
var S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED");
// Filter the imagery collection by date, location, and apply cloud mask
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

// Function to compute statistics for parcels under 'Convencional' management

var stats = dataset.map(function(image) {
  return convencional.map(function(f){
    var mean = image.reduceRegion({reducer: ee.Reducer.mean(),geometry: f.geometry(),scale: 20});
    var std = image.reduceRegion({reducer: ee.Reducer.stdDev(),geometry: f.geometry(),scale: 20});
    return f.set({
      'date': image.date().format(),
      // MEDIA
      'NDSVI_mean': mean.get('NDSVI'),'NDI7_mean': mean.get('NDI7'),
      'NDTI_mean': mean.get('NDTI'),'STI_mean': mean.get('STI'),
      'RATIO_mean': mean.get('RATIO'),'DFI_mean': mean.get('DFI'),
      'SINDRI_mean': mean.get('SINDRI'),
      // STD
      'NDSVI_std': std.get('NDSVI'),'NDI7_std':std.get('NDI7'),
      'NDTI_std': std.get('NDTI'),'STI_std': std.get('STI'),
      'RATIO_std': std.get('RATIO'),'DFI_std': std.get('DFI'),
      'SINDRI_std': std.get('SINDRI')
    });
  });
})
.flatten()
// Filter out parcels with missing index values
.filter(ee.Filter.neq('NDSVI_mean', null)).filter(ee.Filter.neq('NDI7_mean', null))
.filter(ee.Filter.neq('NDTI_mean', null)).filter(ee.Filter.neq('STI_mean', null))
.filter(ee.Filter.neq('RATIO_mean', null)).filter(ee.Filter.neq('DFI_mean', null))
.filter(ee.Filter.neq('SINDRI_mean', null))
.filter(ee.Filter.neq('NDSVI_std', null)).filter(ee.Filter.neq('NDI7_std', null))
.filter(ee.Filter.neq('NDTI_std', null)).filter(ee.Filter.neq('STI_std', null))
.filter(ee.Filter.neq('RATIO_std', null)).filter(ee.Filter.neq('DFI_std', null))
.filter(ee.Filter.neq('SINDRI_std', null));

// Export statistics to Google Drive for 'Convencional' management
Export.table.toDrive({
  collection: stats,
  description: 'Comarca_III_indices_S2_convencional',
  fileFormat: 'CSV',
  folder: 'Proyecto_ReSag'
}); 

// Repeat the process for 'Conservacion' management
var stats = dataset.map(function(image) {
  return conservacion.map(function(f){
    var mean = image.reduceRegion({reducer: ee.Reducer.mean(),geometry: f.geometry(),scale: 20});
    var std = image.reduceRegion({reducer: ee.Reducer.stdDev(),geometry: f.geometry(),scale: 20});
    return f.set({
      'date': image.date().format(),
      'NDSVI_mean': mean.get('NDSVI'),'NDI7_mean': mean.get('NDI7'),
      'NDTI_mean': mean.get('NDTI'),'STI_mean': mean.get('STI'),
      'RATIO_mean': mean.get('RATIO'),'DFI_mean': mean.get('DFI'),
      'SINDRI_mean': mean.get('SINDRI'),
      // STD
      'NDSVI_std': std.get('NDSVI'),'NDI7_std': std.get('NDI7'),
      'NDTI_std': std.get('NDTI'),'STI_std': std.get('STI'),
      'RATIO_std': std.get('RATIO'),'DFI_std':  std.get('DFI'),
      'SINDRI_std':  std.get('SINDRI')
    });
  });
})
.flatten()

.filter(ee.Filter.neq('NDSVI_mean', null)).filter(ee.Filter.neq('NDI7_mean', null))
.filter(ee.Filter.neq('NDTI_mean', null)).filter(ee.Filter.neq('STI_mean', null))
.filter(ee.Filter.neq('RATIO_mean', null)).filter(ee.Filter.neq('DFI_mean', null))
.filter(ee.Filter.neq('SINDRI_mean', null))

.filter(ee.Filter.neq('NDSVI_std', null)).filter(ee.Filter.neq('NDI7_std', null))
.filter(ee.Filter.neq('NDTI_std', null)).filter(ee.Filter.neq('STI_std', null))
.filter(ee.Filter.neq('RATIO_std', null)).filter(ee.Filter.neq('DFI_std', null))
.filter(ee.Filter.neq('SINDRI_std', null));


// Export
Export.table.toDrive({
  collection: stats,
  description: 'Comarca_III_indices_S2_conservacion',
  fileFormat: 'CSV',
  folder: 'Proyecto_ReSag'
}); 



