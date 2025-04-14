// Denna klass hanterar visning av olyckor på Leaflet-kartan
export class AccidentLayer {
  constructor(map) {
    this.map = map;

    // Skapar kluster för olyckor
    this.clusterGroup = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
        const count = cluster.getChildCount();
        return L.divIcon({
          html: `
            <div class="accident-cluster">
              <i class="bi bi-exclamation-triangle-fill"></i><br>
              <span>${count}</span>
            </div>
          `,
          className: 'accident-cluster',
          iconSize: null
        });
      }
    });

    this.loadData(); // Laddar olycksdata direkt
  }

  // Hämtar och visar olyckor på kartan
  async loadData() {
    try {
      const response = await fetch('/accidents');
      const accidents = await response.json();

      // Definierar ikon för olycka
      const accidentIcon = L.divIcon({
        className: 'accident-icon',
        html: '<i class="bi bi-exclamation-triangle-fill"></i>',
        iconSize: null
      });

      // Går igenom varje olycka och lägger till markör
      accidents.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          const marker = L.marker([item.lng, item.lat], { icon: accidentIcon });

          // Skapar popup med information om olyckan
          marker.bindPopup(`
            <div class="accident-popup">
              <h5><i class="bi bi-exclamation-triangle-fill"></i> Olycka</h5>
              <p><strong>${item.location || "Okänd plats"}</strong></p>
              <div style="background-color: red; color: white; padding: 4px; font-weight: bold; text-align: center;">
                ${item.severity || "Okänd påverkan"}
              </div>
              <p><strong>Starttid:</strong> ${item.start ? new Date(item.start).toLocaleString() : "Okänt"}</p>
              <p><strong>Sluttid:</strong> ${item.end ? new Date(item.end).toLocaleString() : "Okänt"}</p>
              <p>${item.message}</p>
            </div>
          `);

          this.clusterGroup.addLayer(marker);
        }
      });

      // Lägger till alla markörer på kartan
      this.map.addLayer(this.clusterGroup);
    } catch (error) {
      console.error("Kunde inte hämta olyckor:", error);
    }
  }
}
