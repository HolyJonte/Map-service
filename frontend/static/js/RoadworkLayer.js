// Den här klassen `RoadworkLayer` skapar ett lager av vägarbeten på en Leaflet-karta.
// Vägarbetena hämtas från API:et `/roadworks` och visas som markörer.
// Markörerna grupperas i kluster med hjälp av Leaflet.markercluster.
// Varje vägarbete visas med en Bootstrap-ikon.
// Om flera vägarbeten är nära varandra, visas de som en större ikon med antal inuti.
// ---------------------------------------------


// Exporterar klassen RoadworkLayer så att den kan användas i andra moduler
export class RoadworkLayer {
  constructor(map) {
    this.map = map;

    // Skapar kluster för vägarbeten
    this.clusterGroup = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
        const count = cluster.getChildCount();
        return L.divIcon({
          html: `
            <div class="custom-roadwork-cluster">
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
        className: 'custom-roadwork-icon', // CSS-klass för styling
        html: '<i class="bi bi-cone-striped"></i>',
        iconAnchor: [10, 20],   // X: mitten av ikonen, Y: nedre kant
        popupAnchor: [-4, -25]  // justering för att popup rutan ska hamna exakt ovanför ikonen
      });

      // Gå igenom varje vägarbete och placera markör på kartan
      roadworks.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          // Skapar markör
          const marker = L.marker([item.lng, item.lat], { icon: roadworkIcon });

          // ===================================================================================================
          // Denna del gör så att texten i popup rutan ändrar färg beroende på hur allvarlig trafikpåverkan är.
          // ===================================================================================================
          let severityText = item.severity || "Okänd påverkan";
          let severityClass = "impact-unknown"; // default

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

          // Innehållet i popup rutan, alltså när man klickar på ett vägarbete.
          marker.bindPopup(`
            <div class="accident-popup">
              <h5><i class="bi bi-cone-striped"></i> Vägarbete</h5>
              <p><strong>${item.location || "Okänd plats"}</strong></p>
              <div class="impact-box ${severityClass}">
                ${severityText}
              </div>
              <p><strong>Starttid:</strong> ${item.start ? new Date(item.start).toLocaleString() : "Okänt"}</p>
              <p><strong>Beräknad sluttid:</strong> ${item.end ? new Date(item.end).toLocaleString() : "Okänt"}</p>
              <p><strong>Beskrivning:</strong> ${item.message || "Ingen beskrivning"}</p>
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
