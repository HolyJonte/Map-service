export class AccidentLayer {
  constructor(map) {
    this.map = map;

    // Skapar klustergrupp
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

    // Lägger till klustret i kartan
    this.map.addLayer(this.clusterGroup);

    // Laddar initial data
    this.loadData();

    // Laddar data var 60:e sekund
    this.interval = setInterval(() => {
      this.loadData();
    }, 60000); // 60000 ms = 60 seka
  }

  // Hämtar och visar olyckor på kartan
  async loadData() {
    try {
      const response = await fetch('/accidents');
      const accidents = await response.json();

      // Rensar gamla markörer
      this.clusterGroup.clearLayers();

      const accidentIcon = L.divIcon({
        className: 'accident-icon',
        html: '<i class="bi bi-exclamation-triangle-fill"></i>',
        iconSize: null
      });

      // Lägg till nya markörer
      accidents.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          const marker = L.marker([item.lng, item.lat], { icon: accidentIcon });

          marker.bindPopup(`
            <div class="accident-popup">
              <h5><i class="bi bi-exclamation-triangle-fill"></i> Olycka</h5>
              <p><strong>${item.location || "Okänd plats"}</strong></p>
              <div style="background-color: red; color: white; padding: 4px; font-weight: bold; text-align: center;">
                ${item.severity || "Okänd påverkan"}
              </div>
              <p><strong>Starttid:</strong> ${item.start ? new Date(item.start).toLocaleString() : "Okänt"}</p>
              <p><strong>Beräknad sluttid:</strong> ${item.end ? new Date(item.end).toLocaleString() : "Okänt"}</p>
              <p>${item.message}</p>
            </div>
          `);

          this.clusterGroup.addLayer(marker);
        }
      });
    } catch (error) {
      console.error("Kunde inte hämta olyckor:", error);
    }
  }
}
