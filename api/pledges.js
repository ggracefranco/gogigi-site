export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const BASE_ID = process.env.AIRTABLE_BASE_ID;
  const TOKEN = process.env.AIRTABLE_TOKEN;
  const TABLE = 'Pledges';
  const AURL = 'https://api.airtable.com/v0/' + BASE_ID + '/' + encodeURIComponent(TABLE);

  if (req.method === 'POST') {
    const { name, email, race, charity, perMileAmount, projectedTotal, message } = req.body;
    try {
      const response = await fetch(AURL, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + TOKEN,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          records: [{
            fields: {
              Name: name,
              Email: email,
              Race: race,
              Charity: charity,
              'Per Mile Amount': parseFloat(perMileAmount),
              'Projected Total': parseFloat(projectedTotal),
              'Submitted At': new Date().toISOString().split('T')[0],
              'Message': message || ''
            }
          }]
        })
      });
      const data = await response.json();
      if (data.error) {
        return res.status(400).json({ success: false, error: data.error });
      }
      return res.status(200).json({ success: true, data });
    } catch (error) {
      return res.status(500).json({ success: false, error: error.message });
    }
  }

  if (req.method === 'GET') {
    try {
      const response = await fetch(AURL + '?sort%5B0%5D%5Bfield%5D=Submitted+At&sort%5B0%5D%5Bdirection%5D=desc', {
        headers: { 'Authorization': 'Bearer ' + TOKEN }
      });
      const data = await response.json();
      return res.status(200).json(data);
    } catch (error) {
      return res.status(500).json({ error: error.message });
    }
  }
}
