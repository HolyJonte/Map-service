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
        iconSize: null
      });

      // Gå igenom varje vägarbete och placera markör på kartan
      roadworks.forEach(item => {
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          // Skapar markör
          const marker = L.marker([item.lng, item.lat], { icon: roadworkIcon });

          // ===========================
          // NY KOD FÖR FÄRGAD PÅVERKAN
          // ===========================
          // === Klassbaserad färg (i stället för inline-färg)
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

          // Popup med samma stil som olyckorna
          marker.bindPopup(`
            <div class="accident-popup">
              <h5><i class="bi bi-cone-striped"></i> Vägarbete</h5>
              <p><strong>${item.location || "Okänd plats"}</strong></p>
              <div class="impact-box ${severityClass}">
                ${severityText}
              </div>
              <p><strong>Starttid:</strong> ${item.start ? new Date(item.start).toLocaleString() : "Okänt"}</p>
              <p><strong>Beräknad sluttid:</strong> ${item.end ? new Date(item.end).toLocaleString() : "Okänt"}</p>
              <p>${item.message || "Ingen beskrivning"}</p>
            </div>
          `);
          // ===========================
          // SLUT PÅ NY KOD
          // ===========================

          this.clusterGroup.addLayer(marker); // Lägg till i klustret
        }
      });

      this.map.addLayer(this.clusterGroup); // Visa alla vägarbetsmarkörer
    } catch (error) {
      console.error("Kunde inte hämta vägarbeten:", error); // Felhantering
    }
  }
}
