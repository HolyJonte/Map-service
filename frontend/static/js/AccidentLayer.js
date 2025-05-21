// Den här klassen `AccidentLayer` skapar ett lager av olyckor på en Leaflet-karta.
// Olyckorna hämtas från API:et `/accidents` och visas som markörer.
// Markörerna grupperas i kluster med hjälp av Leaflet.markercluster.
// Varje olycka visas med en Bootstrap-ikon.
// Om flera olyckor är nära varandra, visas de som en större ikon med antal inuti.
// ---------------------------------------------



// Exporterar klassen AccidentLayer så att den kan användas i andra moduler
export class AccidentLayer {
  constructor(map) {
    this.map = map;

    // Skapar klustergrupp
    this.clusterGroup = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
        const count = cluster.getChildCount();

        // Skapar en anpassad ikon för klustret
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

    // Laddar data var 60:e sekund (lagom för att inte överbelasta servern)
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

      // Skapar en anpassad ikon för olyckor
      const accidentIcon = L.divIcon({
        className: 'custom-accident-icon',
        html: '<i class="bi bi-exclamation-triangle-fill"></i>',
        iconAnchor: [10, 20],     // X: mitten av ikonen, Y: nedrekant
        popupAnchor: [-4, -25]    // justering för att popup rutan ska hamna exakt ovanför ikonen
      });

      // Lägg till nya markörer
      accidents.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          const marker = L.marker([item.lng, item.lat], { icon: accidentIcon });

          // ===================================================================================================
          // Denna del gör så att texten i popup rutan ändrar färg beroende på hur allvarlig trafikpåverkan är.
          // ===================================================================================================
          let severityText = item.severity || "Okänd påverkan";
          let severityClass = "impact-unknown"; // Default

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

          // Innehållet i popup rutan, alltså när man klickar på en olycka.
          marker.bindPopup(`
            <div class="accident-popup">
              <h5><i class="bi bi-exclamation-triangle-fill"></i> Olycka</h5>
              <p><strong>${item.location || "Okänd plats"}</strong></p>
              <div class="impact-box ${severityClass}">
                ${severityText}
              </div>
              <p><strong>Starttid:</strong> ${item.start ? new Date(item.start).toLocaleString() : "Okänt"}</p>
              <p><strong>Beräknad sluttid:</strong> ${item.end ? new Date(item.end).toLocaleString() : "Okänt"}</p>
              <p><strong>Beskrivning:</strong> ${item.message}</p>
            </div>
          `);

          this.clusterGroup.addLayer(marker); // // Lägg till i klustret
        }
      });
    } catch (error) {
      console.error("Kunde inte hämta olyckor:", error); // Felhantering
    }
  }
}
