export class AccidentLayer {
  constructor(map) {
    this.map = map;
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

    this.loadData();
  }

  async loadData() {
    try {
      console.log("🚨 Hämtar olyckor...");
      const response = await fetch('/accidents');
      const accidents = await response.json();
      console.log("🚨 Antal olyckor hämtade:", accidents.length);

      const accidentIcon = L.divIcon({
        className: 'accident-icon',
        html: '<i class="bi bi-exclamation-triangle-fill"></i>',
        iconSize: null
      });

      accidents.forEach(item => {
        console.log("👉 Bearbetar olycka:", item);
        if (!isNaN(item.lat) && !isNaN(item.lng)) {
          const marker = L.marker([item.lng, item.lat], { icon: accidentIcon });
          console.log("✅ Marker lagd på:", item.lat, item.lng);

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

      this.map.addLayer(this.clusterGroup);
    } catch (error) {
      console.error("Kunde inte hämta olyckor:", error);
    }
  }
}
