export class RoadworkLayer {
  constructor(map) {
    this.map = map;
    this.clusterGroup = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
        const count = cluster.getChildCount();
        return L.divIcon({
          html: `
            <div class="roadwork-cluster">
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

      if (!Array.isArray(roadworks)) {
        throw new Error("Fel format på vägarbetsdata: " + JSON.stringify(roadworks));
      }

      const roadworkIcon = L.divIcon({
        className: 'roadwork-icon',
        html: '<i class="bi bi-cone-striped"></i>',
        iconSize: null
      });

      roadworks.forEach(work => {
        if (!isNaN(work.lat) && !isNaN(work.lng)) {
          const marker = L.marker([work.lat, work.lng], { icon: roadworkIcon });

          marker.bindPopup(`
            <div class="roadwork-popup">
              <h5><i class="bi bi-cone-striped"></i> Vägarbete</h5>
              <p><strong>${work.location}</strong></p>
              <div style="background-color: goldenrod; color: white; padding: 4px; font-weight: bold; text-align: center;">
                ${work.severity || "Okänd påverkan"}
              </div>
              <p style="margin-top: 6px;"><strong>Begränsningar:</strong></p>
              <ul>
                ${work.restrictions ? work.restrictions.map(r => `<li>${r}</li>`).join('') : '<li>Ingen info</li>'}
              </ul>
              <p><strong>Starttid:</strong> ${work.start ? new Date(work.start).toLocaleString() : 'Okänt'}</p>
              <p><strong>Sluttid:</strong> ${work.end ? new Date(work.end).toLocaleString() : 'Okänt'}</p>
              <p>${work.description}</p>
            </div>
          `);

          this.clusterGroup.addLayer(marker);
        } else {
          console.error(`Ogiltiga koordinater för vägarbete: ${work.description}`);
        }
      });

      this.map.addLayer(this.clusterGroup);
    } catch (error) {
      console.error("Kunde inte hämta vägarbeten:", error);
    }
  }
}
