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

        // Kontrollera koordinater för att säkerställa att de ligger inom Sverige
        cameras.forEach(camera => {
          // Kontrollera om latitud och longitud är giltiga
          if (!isNaN(camera.lat) && !isNaN(camera.lng)) {
            const marker = L.marker([camera.lng, camera.lat], { icon: cameraIcon });
            marker.bindPopup(`<strong>${camera.name}</strong>`);
            this.clusterGroup.addLayer(marker);  // Lägg till markören i klustret
          } else {
            console.error(`Ogiltig latitud eller longitud för kamera: ${camera.name}`);
          }
        });
        // Lägg till markörklustret på kartan
        this.map.addLayer(this.clusterGroup);

        this.map.setView([62.0, 15.0], 6);  // Centrerad på Sverige med zoomnivå 6
      } catch (error) {
        console.error("Kunde inte hämta kameradata:", error);
      }
    }
  }
