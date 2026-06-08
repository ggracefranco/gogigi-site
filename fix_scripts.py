with open('index.html', 'r') as f:
    content = f.read()

script_start = content.find('<script>')
html_before_script = content[:script_start]

clean_script = """<script>
  function openMenu() {
    document.getElementById('mobileMenu').classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    document.getElementById('mobileMenu').classList.remove('open');
    document.body.style.overflow = '';
  }

  function updateTimers() {
    const now = new Date();
    const races = [
      { date: new Date('2026-08-09T07:00:00'), d: 'd0', h: 'h0', m: 'm0', phrase: 'race0phrase' },
      { date: new Date('2026-09-19T07:00:00'), d: 'd1', h: 'h1', m: 'm1', phrase: 'race1phrase' }
    ];
    const phrases = (days, done) => {
      if (done) return "IT'S RACE DAY! GO ME!! \u{1F9E1}";
      if (days <= 13) return "Okay this is getting real";
      if (days <= 29) return "Lance please answer your phone";
      if (days <= 59) return "Carb loading is a sport right?";
      if (days <= 99) return "TikTok triathlon deep dives are getting more specific";
      return "Still time to pretend I didn't sign up for this";
    };
    races.forEach(r => {
      const diff = r.date - now;
      const days = Math.floor(diff / 86400000);
      if (diff > 0) {
        document.getElementById(r.d).textContent = days;
        document.getElementById(r.h).textContent = Math.floor((diff % 86400000) / 3600000);
        document.getElementById(r.m).textContent = Math.floor((diff % 3600000) / 60000);
      } else {
        document.getElementById(r.d).textContent = '🎉';
        document.getElementById(r.h).textContent = '';
        document.getElementById(r.m).textContent = '';
      }
      const el = document.getElementById(r.phrase);
      if (el) el.textContent = phrases(days, diff <= 0);
    });
  }
  updateTimers();
  setInterval(updateTimers, 30000);

  function selectPledge(el) {
    document.querySelectorAll('.pledge-amt').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
  }

  function handleSignup() {
    const email = document.getElementById('signupEmail').value.trim();
    if (!email || !email.includes('@')) {
      document.getElementById('signupEmail').style.borderColor = 'rgba(232,104,74,0.6)';
      return;
    }
    document.getElementById('emailSuccess').style.display = 'block';
    document.getElementById('signupName').style.display = 'none';
    document.getElementById('signupEmail').style.display = 'none';
    document.querySelector('.email-btn').style.display = 'none';
  }

  async function loadMiles() {
    try {
      const res = await fetch('/api/strava');
      const weeks = await res.json();
      let swim = 0, bike = 0, run = 0;
      Object.keys(weeks).filter(k => k >= '2026-05-03').forEach(week => {
        swim += (weeks[week].swim && weeks[week].swim.distance) || 0;
        bike += (weeks[week].bike && weeks[week].bike.distance) || 0;
        run += (weeks[week].run && weeks[week].run.distance) || 0;
      });
      const total = swim + bike + run;
      function animateCount(id, target) {
        const el = document.getElementById(id);
        if (!el) return;
        const duration = 1500;
        const start = performance.now();
        function update(time) {
          const progress = Math.min((time - start) / duration, 1);
          const ease = 1 - Math.pow(1 - progress, 3);
          el.textContent = (target * ease).toFixed(1);
          if (progress < 1) requestAnimationFrame(update);
          else el.textContent = target.toFixed(1);
        }
        requestAnimationFrame(update);
      }
      const observer = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
          animateCount('swimMiles', swim);
          animateCount('bikeMiles', bike);
          animateCount('runMiles', run);
          animateCount('totalMiles', total);
          observer.disconnect();
        }
      }, { threshold: 0.5 });
      const el = document.getElementById('swimMiles');
      if (el) observer.observe(el);
    } catch(e) { console.log('miles error', e); }
  }

  async function loadTraining() {
    try {
      const res = await fetch('/api/strava');
      const weeks = await res.json();
      const weekKeys = Object.keys(weeks).filter(k => k >= '2026-05-03').sort();
      if (weekKeys.length === 0) {
        document.getElementById('trainingLog').innerHTML = '<p style="color:var(--muted)">No training data yet!</p>';
        return;
      }
      let html = '<div class="training-table-wrap"><table class="training-table"><thead><tr><th>Week</th><th>🏊 Swim</th><th>🚴 Bike</th><th>🏃 Run</th><th>💪 Strength</th></tr></thead><tbody>';
      weekKeys.forEach((week, i) => {
        const w = weeks[week];
        const fmt = (mins) => mins > 0 ? (Math.floor(mins/60) > 0 ? Math.floor(mins/60) + 'h ' : '') + mins%60 + 'm' : '—';
        const swimDist = parseFloat(w.swim.distance.toFixed(1));
        const bikeDist = parseFloat(w.bike.distance.toFixed(1));
        const runDist = parseFloat(w.run.distance.toFixed(1));
        const strengthTime = w.strength && w.strength.time > 0 ? fmt(w.strength.time) : '—';
        html += '<tr><td><strong>Week ' + (i+1) + '</strong><span class=\\"week-date\\">' + new Date(week).toLocaleDateString('en-US',{month:'short',day:'numeric'}) + '</span></td><td>' + (swimDist > 0 ? swimDist+' mi' : '—') + '<span class=\\"week-time\\">' + fmt(w.swim.time) + '</span></td><td>' + (bikeDist > 0 ? bikeDist+' mi' : '—') + '<span class=\\"week-time\\">' + fmt(w.bike.time) + '</span></td><td>' + (runDist > 0 ? runDist+' mi' : '—') + '<span class=\\"week-time\\">' + fmt(w.run.time) + '</span></td><td>' + strengthTime + '</td></tr>';
      });
      html += '</tbody></table></div>';
      document.getElementById('trainingLog').innerHTML = html;
    } catch(e) {
      document.getElementById('trainingLog').innerHTML = '<p style="color:var(--muted)">Training data loading soon!</p>';
    }
  }

  loadMiles();
  loadTraining();
</script>
</body>
</html>"""

with open('index.html', 'w') as f:
    f.write(html_before_script + clean_script)

print("Done! File size:", len(html_before_script + clean_script))
