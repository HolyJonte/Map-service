// Denna fil innehåller definitionen av MapComponent som är en anpassad HTML-komponent för att visa en karta med ikoner på.
// Kartan centereas över Sverige och innehåller tre olika lager.
// 1. Fartkameror (CameraLayer)
// 2. Vägarbeten (RoadworkLayer)
// 3. Olyckor (AccidentLayer)
// Dessutom finns det en knapp för att hämta användarens plats och visa den på kartan.

//Importerar de olika lagren som används i kartan
import { CameraLayer } from './CameraLayer.js';
import { RoadworkLayer } from './RoadworkLayer.js';
import { AccidentLayer } from './AccidentLayer.js';

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
    this.roadworkLayer = null;
    this.accidentLayer = null;
  }

  // Denna metod anropas när komponenten läggs till i DOM
  connectedCallback() {
    this.innerHTML = `<div id="map"></div>`;
    this.initMap();
  }

  // Denna metod initierar Leaflet-kartan och lägger till fartkameralagret
  initMap() {
    // ⇓ läs av data-attribut från själva <map-component>:
    const lat  = parseFloat(this.dataset.lat)  || 62.0;
    const lng  = parseFloat(this.dataset.lng)  || 15.0;
    const zoom = parseInt(this.dataset.zoom, 10) || 6;
  
    this.map = L.map('map', {
      center: [lat, lng],      // ⇑ använd dynamiskt
      zoom: zoom               // ⇑ använd dynamiskt
    });  

    // Lägg till OpenStreetMap som bakgrundskarta
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 14
    }).addTo(this.map);

    // Skapar ett nytt lager för fartkameror och vägarbeten och kopplar det till kartan
    this.cameraLayer = new CameraLayer(this.map);
    this.roadworkLayer = new RoadworkLayer(this.map);
    setTimeout(() => {
      this.accidentLayer = new AccidentLayer(this.map);
    }, 300); //


// Lägg till "hitta min plats"-knapp
const locateButton = L.control({ position: 'bottomright' });

// Skapa knappen och lägg till den i kartan
locateButton.onAdd = function () {
  // Skapa en div för knappen
  const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');

  // Lägger till iconen för knappen
  div.innerHTML = `<a href="#" title="Hitta min plats" id="locateMeBtn" class="locate-button">
                     <i class="bi bi-geo-alt-fill"></i>
                   </a>`;
  // Returnerar knappen så att det kan läggas till i kartan
  return div;
};

// Lägg till knappen i kartan
locateButton.addTo(this.map);

// Väntar en kort stund så att kanppen hinner laddas innan vi lägger till eventlyssnaren
setTimeout(() => {
  // Hämtar knappen med id "locateMeBtn" och lägger till en eventlyssnare för klick
  const btn = document.getElementById('locateMeBtn');

  // Om knappen finns, lägg till en eventlyssnare för att hämta användarens plats
  if (btn) {
    btn.addEventListener('click', (e) => {
      // Förhindra standardbeteendet för länken (t.ex. att sidan laddas om)
      e.preventDefault();

      // Anropar Leaflet-funktionen för att hämta användarens plats
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

// Om platsen inte kan hittas (tex om användaren nekar åtkomst)
this.map.on('locationerror', (e) => {
  alert("Kunde inte hitta din plats: " + e.message);
});
  }
}

// Registrera komponenten
customElements.define('map-component', MapComponent);