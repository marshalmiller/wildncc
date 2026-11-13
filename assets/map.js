(function () {
  var el = document.getElementById('wildmap');
  if (!el || typeof L === 'undefined') return;
  var c = (el.getAttribute('data-center') || '40.671,-75.323').split(',');
  var map = L.map('wildmap').setView([parseFloat(c[0]), parseFloat(c[1])], 16);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
  var locs;
  try { locs = LOCATIONS || []; } catch (e) { locs = []; }
  var bounds = [];
  locs.forEach(function (mk) {
    if (!mk.lat || !mk.lon) return;
    var m = L.marker([parseFloat(mk.lat), parseFloat(mk.lon)]).addTo(map);
    bounds.push([parseFloat(mk.lat), parseFloat(mk.lon)]);
    var html = '<strong>' + mk.name + '</strong>' +
      (mk.sci ? ' <em>(' + mk.sci + ')</em>' : '') +
      (mk.href ? '<br><a href="' + mk.href + '">View in the guide</a>' : '');
    m.bindPopup(html);
  });
  if (bounds.length) map.fitBounds(bounds, {padding: [24, 24]});
})();
