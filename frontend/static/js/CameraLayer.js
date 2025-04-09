export class CameraLayer {
    constructor(map) {
      this.map = map;
      this.markers = [];
      this.clusterGroup = L.markerClusterGroup({
        iconCreateFunction: function (cluster) {
          const count = cluster.getChildCount();

          return L.divIcon({
            html: `
              <div class="custom-cluster-icon">
                <i class="bi bi-camera-fill"></i><br>
                <span>${count}</span>
              </div>
            `,
            className: 'camera-cluster', // Anpassningsbar för CSS
            iconSize: null // ← styrs av CSS
          });
        }
      });
            this.loadData();
    }

    async loadData() {
      try {
        const response = await fetch('/cameras');
        const cameras = await response.json();

        const cameraIcon = L.divIcon({
          className: 'custom-camera-icon',
          html: '<i class="bi bi-camera-fill"></i>',  // Bootstrap ikon
          iconSize: null // ← styrs helt av CSS
        });

        console.log(`Antal kameror som hämtades: ${cameras.length}`);
        console.log(cameras[0]); // Första kameran

        // Kontrollera koordinater för att säkerställa att de ligger inom Sverige
        cameras.forEach(camera => {
          console.log(`Kamera: ${camera.name}, Lat: ${camera.lat}, Lng: ${camera.lng}`);

          if (camera.lat < 55 || camera.lat > 70 || camera.lng < 10 || camera.lng > 25) {
            console.warn(`Kamera ${camera.name} har koordinater utanför Sverige: Lat: ${camera.lat}, Lng: ${camera.lng}`);
          }

          // Kontrollera om latitud och longitud är giltiga
          if (!isNaN(camera.lat) && !isNaN(camera.lng)) {
            const marker = L.marker([camera.lng, camera.lat], { icon: cameraIcon });
            marker.bindPopup(`<strong>${camera.name}</strong>`);
            this.clusterGroup.addLayer(marker);  // Lägg till markören i klustret
          } else {
            console.error(`Ogiltig latitud eller longitud för kamera: ${camera.name}`);
          }
        });
  
        console.log(`Antal markörer som lagts till i klustret: ${this.clusterGroup.getLayers().length}`);
  
        // Lägg till markörklustret på kartan
        this.map.addLayer(this.clusterGroup);
  
        // Centrera kartan på Sverige och sätt zoomnivån
        this.map.setView([62.0, 15.0], 6);  // Centrerad på Sverige med zoomnivå 6
        console.log("Kartan är centrerad på Sverige");
  
      } catch (error) {
        console.error("Kunde inte hämta kameradata:", error);
      }
    }
  }
  