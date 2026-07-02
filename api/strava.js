let cache = null;
let cacheTime = 0;
const CACHE_DURATION = 15 * 60 * 1000; // 15 minutes

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  // Return cached data if available
  if (cache && Date.now() - cacheTime < CACHE_DURATION) {
    return res.status(200).json(cache);
  }
  
  try {
    const tokenRes = await fetch('https://www.strava.com/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: process.env.STRAVA_CLIENT_ID,
        client_secret: process.env.STRAVA_CLIENT_SECRET,
        refresh_token: process.env.STRAVA_REFRESH_TOKEN,
        grant_type: 'refresh_token'
      })
    });
    
    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;

  const after = Math.floor(new Date('2026-05-03').getTime() / 1000);
    const activitiesRes = await fetch(
      `https://www.strava.com/api/v3/athlete/activities?after=${after}&per_page=100`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );

    const activities = await activitiesRes.json();

   if (!Array.isArray(activities)) {
      return res.status(200).json({ error: 'not an array', activities });
    }

    const weeks = {};
    activities.forEach(activity => {
      const date = new Date(activity.start_date);
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - ((date.getDay() + 6) % 7));
      const weekKey = weekStart.toISOString().split('T')[0];
      
      if (!weeks[weekKey]) {
        weeks[weekKey] = { 
          swim: { distance: 0, time: 0 }, 
          bike: { distance: 0, time: 0 }, 
          run: { distance: 0, time: 0 },
          strength: { time: 0 }
        };
      }
      
      const miles = parseFloat((activity.distance / 1609.34).toFixed(2));
      const mins = Math.round(activity.moving_time / 60);
      const type = activity.type;

      if (type === 'Swim') {
        weeks[weekKey].swim.distance += miles;
        weeks[weekKey].swim.time += mins;
      } else if (type === 'Ride' || type === 'VirtualRide') {
        weeks[weekKey].bike.distance += miles;
        weeks[weekKey].bike.time += mins;
      } else if (type === 'Run' || type === 'Walk') {
        weeks[weekKey].run.distance += miles;
        weeks[weekKey].run.time += mins;
      } else if (type === 'WeightTraining' || type === 'Yoga') {
        weeks[weekKey].strength.time += mins;
      }
    });

    cache = weeks;
    cacheTime = Date.now();
    res.status(200).json(weeks);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
