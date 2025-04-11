export class RoadworkLayer {
  constructor(map) {
    this.map = map;
    this.clusterGroup = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
        const count = cluster.getChildCount();
        return L.divIcon({
          html: `
            <div class="custom-cluster-icon">
              <i class="bi bi-cone-striped"></i><br>
              <span>${count}</span>
            </div>
          `,
          className: 'roadwork-cluster',
          iconSize: null
        });
      }
    });
    this.loadData();
  }

  async loadData() {
    try {
      const response = await fetch('/roadworks');
      const roadworks = await response.json();

      const roadworkIcon = L.divIcon({
        className: 'custom-camera-icon', // Återanvänder kamerastil för ikonen
        html: '<i class="bi bi-cone-striped"></i>',
        iconSize: null
      });

      roadworks.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          const marker = L.marker([item.lng, item.lat], { icon: roadworkIcon });


          marker.bindPopup(`
            <p><strong>${item.location}</strong></p>
            <strong>Vägarbete</strong><br>${item.message}
          `);


          this.clusterGroup.addLayer(marker);
        }
      });

      this.map.addLayer(this.clusterGroup);
    } catch (error) {
      console.error("Kunde inte hämta vägarbeten:", error);
    }
  }
}