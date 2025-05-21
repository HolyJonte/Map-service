// Den här klassen `CameraLayer` skapar ett lager av fartkameror på en Leaflet-karta.
// Kamerorna hämtas från API:et `/cameras` och visas som markörer.
// Markörerna grupperas i kluster med hjälp av Leaflet.markercluster.
// Varje kamera visas med en Bootstrap-ikon.
// Om flera kameror är nära varandra, visas de som en större ikon med antal inuti.
// ---------------------------------------------


// Exporterar klassen för användning i andra moduler
export class CameraLayer {
    constructor(map) {
      this.map = map;       // Referens till Leaflet-kartan
      this.markers = [];    // Lista för enskilda markörer

      // Skapar ett klusterobjekt för markörer
      this.clusterGroup = L.markerClusterGroup({
        iconCreateFunction: function (cluster) {
          const count = cluster.getChildCount();    // Antal kameror i klustret

          // Returnerar en anpassad HTML-ikon för klustret
          return L.divIcon({
            html: `
              <div class="custom-camera-cluster">
                <i class="bi bi-camera-fill"></i><br>
                <span>${count}</span>
              </div>
            `,
            className: 'camera-cluster',    // Anpassningsbar för CSS
            iconSize: null    // Storleken styrs med CSS istället för här
          });
        }
      });
            this.loadData();    // Laddar in kameradatan direkt vid skapande av objektet
    }


    // -----------------------------
    // Funktion som hämtar kameradata och lägger till markörer på kartan
    // -----------------------------
    async loadData() {
      try {
        const response = await fetch('/cameras');     // Hämtar kameradata från API:et
        const cameras = await response.json();        // Konverterar svaret till JSON

        // Skapa en ikon för varje kamera (Bootstrap-kameraikon)
        const cameraIcon = L.divIcon({
          className: 'custom-camera-icon',
          html: '<i class="bi bi-camera-fill"></i>',
          iconAnchor: [10, 20],     // X: mitten av ikonen, Y: nedre kant
          popupAnchor: [-4, -25]    // justering för att popup rutan ska hamna exakt ovanför ikonen
        });

        // Kontrollera koordinater för att säkerställa att de ligger inom Sverige
        // Gå igenom varje kamera och skapa en markör
        cameras.forEach(camera => {
          // Kontrollera om latitud och longitud är giltiga
          if (!isNaN(camera.lat) && !isNaN(camera.lng)) {
            const marker = L.marker([camera.lng, camera.lat], { icon: cameraIcon });

            // Visa namnet och vägnummer i en popup
            marker.bindPopup(`
              <div class="accident-popup">
                <h5><i class="bi bi-camera-fill"></i> Fartkamera</h5>
                <p><strong>${camera.name}</strong></p>
                <p>Vägnummer: ${camera.road}</p>
              </div>
            `);

            // Lägg till markören i klustret
            this.clusterGroup.addLayer(marker);
          } else {
            // Om koordinater saknas eller är ogiltiga, logga ett fel
            console.error(`Ogiltig latitud eller longitud för kamera: ${camera.name}`);
          }
        });
        // Lägg till markörklustret på kartan
        this.map.addLayer(this.clusterGroup);

      // Logga eventuella fel vid hämtning av data
      } catch (error) {
        console.error("Kunde inte hämta kameradata:", error);
      }
    }
  }
