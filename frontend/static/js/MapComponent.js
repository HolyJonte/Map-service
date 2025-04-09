// Importera fartkameralagret
import { CameraLayer } from './CameraLayer.js';

class MapComponent extends HTMLElement {
  constructor() {
    super();
    this.map = null;         // Här sparas Leaflet-kartan
    this.cameraLayer = null; // Här sparas kameralagret
  }

  // Körs automatiskt när <map-component> läggs in i DOM
  connectedCallback() {
    this.innerHTML = `<div id="map" style="height: 80vh;"></div>`; // Kartan tar upp 80% av höjden
    this.initMap();  // Starta kartan
  }

  // Initierar Leaflet-kartan och laddar fartkamerorna
  initMap() {
    // Skapa Leaflet-karta centrerad över Sverige
    this.map = L.map('map').setView([62.0, 15.0], 5);

    // Lägg till OpenStreetMap-kaklayer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(this.map);

    // Skapa fartkameralagret och ladda datan
    this.cameraLayer = new CameraLayer(this.map);
    this.cameraLayer.loadData();
  }
}

// Registrera komponenten så <map-component> fungerar i HTML
customElements.define('map-component', MapComponent);
