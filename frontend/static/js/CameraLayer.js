// Den här klassen `CameraLayer` skapar ett lager av fartkameror på en Leaflet-karta.
// Kamerorna hämtas från API:et `/cameras` och visas som markörer.
// Markörerna grupperas i kluster med hjälp av Leaflet.markercluster.
// Varje kamera visas med en Bootstrap-ikon.
// Om flera kameror är nära varandra, visas de som en större ikon med antal inuti.
// ---------------------------------------------

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
              <div class="custom-cluster-icon">
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
          html: '<i class="bi bi-camera-fill"></i>',  // Bootstrap ikon
          iconSize: null                              // Storlek styrs av CSS
        });

        // Kontrollera koordinater för att säkerställa att de ligger inom Sverige
        // Gå igenom varje kamera och skapa en markör
        cameras.forEach(camera => {
          // Kontrollera om latitud och longitud är giltiga
          if (!isNaN(camera.lat) && !isNaN(camera.lng)) {
            const marker = L.marker([camera.lng, camera.lat], { icon: cameraIcon });

            // Visa namnet och vägnummer i en popup
            marker.bindPopup(`
              <strong>${camera.name}</strong><br>
              Vägnummer: ${camera.road}
            `);

            this.clusterGroup.addLayer(marker);                   // Lägg till markören i klustret
          } else {
            // Om koordinater saknas eller är ogiltiga, logga ett fel
            console.error(`Ogiltig latitud eller longitud för kamera: ${camera.name}`);
          }
        });
        // Lägg till markörklustret på kartan
        this.map.addLayer(this.clusterGroup);

        // Flytta kartan så att den visar hela Sverige
        this.map.setView([62.0, 15.0], 6);  // Centrerad på Sverige med zoomnivå 6

      } catch (error) {
        // Om något går fel med hämtning av data, visa fel i konsolen
        console.error("Kunde inte hämta kameradata:", error);
      }
    }
  }
