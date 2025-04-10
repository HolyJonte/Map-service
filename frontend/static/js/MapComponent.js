// Denna fil innehåller definitionen av MapComponent som är en anpassad HTML-komponent för att visa en karta med fartkameror.
// Kartan centereas över Sverige och innehåller en lager för fartkameror.


//Importerar fartkameralagret som är definierat i CameraLayer.js
import { CameraLayer } from './CameraLayer.js';  // Se till att sökvägen är korrekt

// Definierar en ny klass för komponenten map-component
// Denna klass ärver från HTMLElement och representerar en anpassad HTML-komponent
class MapComponent extends HTMLElement {
  // Konstuktorn för komponenten
  constructor() {
    // Anropar superklassen konstruktor
    super();
    // Här lagras Leaflet-kartan
    this.map = null;
    // Här lagras fartkameralagret
    this.cameraLayer = null;
  }

  // Denna metod anropas när komponenten läggs till i DOM
  connectedCallback() {
    this.innerHTML = `<div id="map" style="height: 80vh;"></div>`;
    this.initMap();
  }

  // Denna metod initierar Leaflet-kartan och lägger till fartkameralagret
  initMap() {
    this.map = L.map('map', {
      center: [62.0, 15.0],  // Centrera kartan på Sverige
      zoom: 6                // Zoomnivå för att visa Sverige
    });

    // Lägg till OpenStreetMap som bakgrundskarta
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(this.map);

    // Skapar ett nytt lager för fartkameror och kopplar det till kartan
    this.cameraLayer = new CameraLayer(this.map);
    // Laddar data för fartkamerorna
    this.cameraLayer.loadData();



// =============================================================
// Kod som inte är testat än:
// =============================================================
// Lägg till "hitta min plats"-knapp
const locateButton = L.control({ position: 'bottomright' });

locateButton.onAdd = function () {
  const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
  div.innerHTML = `<a href="#" title="Hitta min plats" id="locateMeBtn" class="locate-button">
                     <i class="bi bi-geo-alt-fill"></i>
                   </a>`;
  return div;
};

locateButton.addTo(this.map);

// Eventlistener för att hitta användarens plats
setTimeout(() => {
  const btn = document.getElementById('locateMeBtn');
  if (btn) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      this.map.locate({ setView: true, maxZoom: 14 });
    });
  }
}, 0);

// När platsen hittas, lägg till markör
this.map.on('locationfound', (e) => {
  const userMarker = L.marker(e.latlng).addTo(this.map)
    .bindPopup("Du är här")
    .openPopup();
});

// Om platsen inte kan hittas
this.map.on('locationerror', (e) => {
  alert("Kunde inte hitta din plats: " + e.message);
});
  }





}







// Registrerar komponenten så att map-component kan användas i HTML
customElements.define('map-component', MapComponent);
