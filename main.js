const pb = document.getElementById('pb');
function updatePb() {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  if (pb && max > 0) pb.style.width = (window.scrollY / max * 100) + '%';
}

function reveal() {
  const els = document.querySelectorAll('.rev');
  const h = window.innerHeight;
  els.forEach(el => {
    if (el.getBoundingClientRect().top < h * 0.94) {
      el.classList.add('on');
    }
  });
}

function parallax() {
  const y = window.scrollY;
  const t = document.querySelector('.hero-title');
  const yr = document.querySelector('.hero-year');
  if (t) t.style.transform = 'translateY(' + (y * 0.09) + 'px)';
  if (yr) yr.style.transform = 'translateX(' + (y * 0.035) + 'px)';
}

window.addEventListener('scroll', function() {
  updatePb(); reveal(); parallax();
}, { passive: true });

window.addEventListener('resize', reveal, { passive: true });

updatePb();
reveal();

var lines = document.querySelectorAll('.hero-title span');
lines.forEach(function(el, i) {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  setTimeout(function() {
    el.style.opacity = '1';
    el.style.transform = 'none';
  }, 100 + i * 90);
});

document.querySelectorAll('.model-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const model = tab.dataset.model;

    document.querySelectorAll('.model-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    document.querySelectorAll('.model-frame').forEach(frame => {
      if (frame.dataset.model === model) {
        if (!frame.src && frame.dataset.src) frame.src = frame.dataset.src; // lazy load
        frame.classList.add('active');
      } else {
        frame.classList.remove('active');
      }
    });
  });
});
