// Denna klass hanterar visning av vägarbeten på Leaflet-kartan
export class RoadworkLayer {
  constructor(map) {
    this.map = map;

    // Skapar kluster för vägarbeten
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

    this.loadData(); // Laddar vägarbetsdata direkt
  }

  // Hämtar vägarbetsdata från API och visar dem som markörer på kartan
  async loadData() {
    try {
      const response = await fetch('/roadworks');
      const roadworks = await response.json();

      // Ikon för vägarbete (med Bootstrap-kon)
      const roadworkIcon = L.divIcon({
        className: 'custom-camera-icon', // CSS-klass för styling
        html: '<i class="bi bi-cone-striped"></i>',
        iconSize: null
      });

      // Gå igenom varje vägarbete och placera markör på kartan
      roadworks.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          // OBS: lat/lng är omkastade i koordinatsystemet här
          const marker = L.marker([item.lng, item.lat], { icon: roadworkIcon });

          // Popup med information om vägarbetet
          marker.bindPopup(`
            <div class="roadwork-popup">
              <p><strong>${item.location || "Okänd plats"}</strong></p>
              <strong>Vägarbete</strong><br>
              ${item.message || "Ingen beskrivning"}<br><br>
              <strong>Påverkan:</strong> ${item.severity || "Okänd påverkan"}<br>
              <strong>Starttid:</strong> ${item.start ? new Date(item.start).toLocaleString() : "Okänt"}<br>
              <strong>Sluttid:</strong> ${item.end ? new Date(item.end).toLocaleString() : "Okänt"}<br>
            </div>
          `);

          this.clusterGroup.addLayer(marker); // Lägg till i klustret
        }
      });

      this.map.addLayer(this.clusterGroup); // Visa alla vägarbetsmarkörer
    } catch (error) {
      console.error("Kunde inte hämta vägarbeten:", error); // Felhantering
    }
  }
}
