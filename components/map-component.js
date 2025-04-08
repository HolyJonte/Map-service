// Web component som visar kartan med Leaflet
export class MapComponent extends HTMLElement {
    constructor() {
      super();
      this.map = null;
    }

    connectedCallback() {
      this.innerHTML = `<div id="map" style="height: 600px;"></div>`;
      this.initMap();
    }

    initMap() {
      // Initiera Leaflet-karta
      this.map = L.map('map').setView([62.0, 15.0], 5); // Centrera över Sverige

      // Lägg till OpenStreetMap tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 18
      }).addTo(this.map);

      // Exempel: Testmarkör
      const marker = L.marker([59.3293, 18.0686]).addTo(this.map);
      marker.bindPopup("Stockholm – Testhändelse").openPopup();
    }
  }

  customElements.define('map-component', MapComponent);
