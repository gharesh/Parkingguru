# Flask-Bootstrap-App

### Run
```
python app.py
```

```
CONNECTION STRING for Mongo Compass
mongodb+srv://n30:infy%40123@democluster-klhmq.mongodb.net/test
```

#REST services
<br>
#GET:<br>
http://localhost:5000/MLCP <br>
http://localhost:5000/MLCP/1  &nbsp;&nbsp;(for specific floor) <br>
<p>
#POST<br>
&nbsp;&nbsp;&nbsp;http://localhost:5000/MLCPFloorInbound &nbsp;&nbsp;&nbsp;&nbsp; (to add new vehicle)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;type: application/json <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; body : {"floorNumber":"1","vehicleNumber":"11zz0011"} <br>
