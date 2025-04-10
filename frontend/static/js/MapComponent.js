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
  }
}

// Registrerar komponenten så att map-component kan användas i HTML
customElements.define('map-component', MapComponent);
