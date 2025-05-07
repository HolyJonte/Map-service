/*
 * subscription_form.js
 
  Hanterar SMS-prenumerationsformuläret:
  - Hämtar och fyller dropdowns för tidningar och län
  - Validerar telefonnummer (+46-format) och obligatoriska fält
  - Initierar och laddar Klarna-betalning
  - Visar order-sammanfattning och hanterar betalningssvar
 */


//Hämtar och fyller dropdown med tidningar från servern
async function loadNewspapers() {
    const select = document.getElementById("newspaper_id");
    try {
      const res = await fetch("/subscriptions/newspapers");
      if (!res.ok) throw new Error("Kunde inte hämta tidningar från servern");
      const newspapers = await res.json();
      select.innerHTML = "";
      const defaultOption = document.createElement("option");
      defaultOption.textContent = "Välj en tidning";
      defaultOption.disabled = true;
      defaultOption.selected = true;
      select.appendChild(defaultOption);
      Object.entries(newspapers).forEach(([id, name]) => {
        const option = document.createElement("option");
        option.value = id;
        option.textContent = name;
        select.appendChild(option);
      });
    } catch (err) {
      console.error("Kunde inte hämta tidningar:", err);
    }
  }
  // Hämtar län och lägger till den i select-elementet
  async function loadCounties() {
  const select = document.getElementById("counties");
  try {
    const res = await fetch("/subscriptions/counties");
    const counties = await res.json();

    // Lägg till placeholder först – exakt som för tidningarna
    const defaultOption = document.createElement("option");
    defaultOption.textContent = "Välj ett län";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    select.appendChild(defaultOption);

    // Lägg till alla län
    const addedCounties = new Set();
    Object.entries(counties).forEach(([code, name]) => {
      if (!addedCounties.has(name)) {
        addedCounties.add(name);
        const option = document.createElement("option");
        option.value = code;
        option.textContent = name;
        select.appendChild(option);
      }
    });
  
  } catch (err) {
    console.error("Kunde inte hämta länslista:", err);
  }
}

  window.onload = function() {
    loadCounties();
    loadNewspapers();
  };
  // Hantering av formulärets submit
  document.getElementById('subscription-form').addEventListener('submit', async (event) => {
    event.preventDefault();

     // Läs in användarens telefonnummer och valda alternativ
    let phoneNumber = document.getElementById('phone_number').value;
    const counties = Array.from(document.getElementById('counties').selectedOptions)
                      .map(option => parseInt(option.value));
    const newspaper_id = document.getElementById('newspaper_id').value;
    const responseDiv = document.getElementById('response');

    phoneNumber = phoneNumber.trim();
    if (!phoneNumber.startsWith('+46')) {
      phoneNumber = phoneNumber.replace(/^0/, '+46');
    }
     // Validera telefonformat
    if (!/^\+46\d{9}$/.test(phoneNumber)) {
      responseDiv.innerHTML = `<p class="error">Ogiltigt telefonnummer. Använd formatet +46701234567.</p>`;
      return;
    }
     // Kontrollera att alla fält är ifyllda
    if (!phoneNumber || counties.length === 0 || !newspaper_id || newspaper_id === "Välj en tidning") {
      responseDiv.innerHTML = `<p class="error">Vänligen fyll i telefonnummer, län och tidning.</p>`;
      return;
    }

    try {
       // Skicka start-subscription till servern
      const response = await fetch('/subscriptions/start-subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phoneNumber,
          counties: counties,
          newspaper_id: parseInt(newspaper_id),
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Spara session och telefon i localStorage
        localStorage.setItem('phoneNumber', phoneNumber);
        localStorage.setItem('klarnaSessionId', data.session_id);
        localStorage.setItem('email', data.email);

        // Bygg och visa order-sammanfattning
        const countySelect = document.getElementById('counties');
        const countyText   = countySelect.options[countySelect.selectedIndex].textContent;

        // 2) Bygg summary-card HTML
        const summaryHtml = `
          <div id="order-summary" class="order-summary-card mt-4">
            <h3>Din prenumeration</h3>
            <p>Du tecknar en SMS-prenumeration för 99 SEK i <strong>${countyText}</strong> för att få uppdateringar om trafikläget i ditt län.</p>
            <p>När du klickar på <em>"Bekräfta köp"</em> kommer du att dirigeras till Klarna för att slutföra betalningen.</p>
          </div>
        `;

        // 3) Infoga summaryHtml precis ovanför Klarna-containern
        const klarnaContainer = document.getElementById('klarna-checkout-container');
        klarnaContainer.insertAdjacentHTML('beforebegin', summaryHtml);
        
         // Initiera Klarna och ladda betalningsformuläret
              Klarna.Payments.init({
                client_id: data.client_id,
                client_token: data.client_token
              });

        // 2) Ladda kort-UI:t med all betalinfo
        Klarna.Payments.load({
          container: '#klarna-checkout-container',
          payment_method_category: 'pay_now',

        }, function(res) {
          if (res.show_form) {
            console.log('Betalningsformulär laddat');
            responseDiv.innerHTML =
              '<p>Om du godkänner prenumerationen dirigeras du till Klarna "Bekräfta köp".</p>';
          } else if (res.error) {
            console.error('Fel vid laddning:', res.error);
            responseDiv.innerHTML =
              `<p class="error">Fel vid laddning: ${res.error}</p>`;
          }
        });


        // Skapa riktig "Betala" knapp
      if (!document.getElementById('klarna-authorize-click')) {
        // Skapa wrapper-div
        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex justify-content-center mt-3';

        // Skapa knappen
        const payBtn = document.createElement('button');
        payBtn.id = 'klarna-authorize-click';
        payBtn.textContent = 'Bekräfta köp';
        payBtn.className = 'klarna-authorize-button';

        // Lägg knappen i wrappern
        wrapper.appendChild(payBtn);

        // Lägg wrappern efter Klarna-container
        document.querySelector('#klarna-checkout-container').after(wrapper);


      // NY kod att klistra in istället:
      if (!document.getElementById('klarna-authorize-click')) {
        // Skapa wrapper-div
        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex justify-content-center mt-3';

        // Skapa knappen
        const payBtn = document.createElement('button');
        payBtn.id = 'klarna-authorize-click';
        payBtn.textContent = 'Bekräfta köp';
        payBtn.className = 'klarna-authorize-button';

        // Lägg knappen i wrappern
        wrapper.appendChild(payBtn);

        // Lägg wrappern efter Klarna-container
        document.querySelector('#klarna-checkout-container').after(wrapper);
      }

        // Lägg till eventlyssnare
        payBtn.addEventListener('click', () => {
          Klarna.Payments.authorize(
            { payment_method_category: 'pay_now' },
            {},
            async function(res) {
              if (res.approved) {
                const sessionId = localStorage.getItem('klarnaSessionId');
                const conf = await fetch('/subscriptions/prenumeration-startad', {
                  method: 'POST',
                  headers: {'Content-Type':'application/json'},
                  body: JSON.stringify({
                    session_id:          sessionId,
                    authorization_token: res.authorization_token
                  })
                });

                if (conf.redirected) {
                  window.location.href = conf.url;
                } else {
                  document.documentElement.innerHTML = await conf.text();
                }
              } else {
                responseDiv.innerHTML = '<p class="error">Betalningen nekades.</p>';
              }
            }
          );
        });
      }

      } else if (!response.ok) {
        // Hantera fel, inklusive already_subscribed
        if (data.error === "already_subscribed") {
          alert("Du är redan prenumerant med detta telefonnummer. Du dirigeras till din profil.");
          setTimeout(() => window.location.href = "/users/profile", 1000);
        } else {
          responseDiv.innerHTML = `<p class="error">Fel: ${data.error || "Okänt fel"}</p>`;
        }
      }
    } catch (error) {
      console.error("Fetch error:", error);
      responseDiv.innerHTML = `<p class="error">Något gick fel: ${error.message}</p>`;
    }
  });