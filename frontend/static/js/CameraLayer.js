// En klass som hanterar fartkameror på Leaflet-kartan
export class CameraLayer {
    constructor(map) {
      this.map = map;                     // Kartinstansen från Leaflet
      this.layer = L.layerGroup().addTo(map);  // Skapar en egen "grupp" för kamerorna
    }

    async loadData() {
      try {
        const response = await fetch('/cameras'); // Anropa din Flask-endpoint
        const data = await response.json();       // Omvandla till JavaScript-objekt

        data.forEach(camera => {
          const marker = L.marker([camera.lat, camera.lng])
            .addTo(this.layer)  // Lägg till varje kamera i LayerGroup
            .bindPopup(`
              <strong>${camera.name}</strong><br>
              Status: ${camera.active ? 'Aktiv' : 'Inaktiv'}
            `);
        });
      } catch (error) {
        console.error("Kunde inte hämta kameradata:", error);
      }
    }
  }
