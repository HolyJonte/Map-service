export class AccidentLayer {
  constructor(map) {
    this.map = map;

    // Skapar klustergrupp
    this.clusterGroup = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
        const count = cluster.getChildCount();

        return L.divIcon({
          html: `
            <div class="custom-accident-cluster">
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
    }, 60000); // 60000 ms = 60 sekunder
  }

  // Hämtar och visar olyckor på kartan
  async loadData() {
    try {
      const response = await fetch('/accidents');
      const accidents = await response.json();

      // Rensar gamla markörer
      this.clusterGroup.clearLayers();

      const accidentIcon = L.divIcon({
        className: 'custom-accident-icon',
        html: '<i class="bi bi-exclamation-triangle-fill"></i>',
        iconSize: null
      });

      // Lägg till nya markörer
      accidents.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          const marker = L.marker([item.lng, item.lat], { icon: accidentIcon });

          // ================================
          // Ny färglogik baserat på påverkan
          // ================================
          let severityText = item.severity || "Okänd påverkan";
          let severityClass = "impact-unknown"; // Standardfärg

          if (severityText.includes("Ingen påverkan")) {
            severityClass = "impact-none";
          } else if (severityText.includes("Liten påverkan")) {
            severityClass = "impact-low";
          } else if (
            severityText.includes("Stor påverkan") ||
            severityText.includes("Mycket stor påverkan")
          ) {
            severityClass = "impact-high";
          }

          // Popup med konsekvent stil (samma som vägarbeten)
          marker.bindPopup(`
            <div class="accident-popup">
              <h5><i class="bi bi-exclamation-triangle-fill"></i> Olycka</h5>
              <p><strong>${item.location || "Okänd plats"}</strong></p>
              <div class="impact-box ${severityClass}">
                ${severityText}
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
