const express = require("express");
const path = require("path");

var MongoClient = require('mongodb').MongoClient,
    Server = require('mongodb').Server,
    bodyParser = require('body-parser')
    fs = require('fs');

var url = "mongodb://localhost:27017/";

var multer = require('multer');
var upload = multer({ dest: 'uploads/' });

var collection, dbObj;
module.exports = {

};

const app = express();

app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded

var exports = module.exports;

app.use(express.static(path.join(__dirname)));
// console.log(path.join(__dirname));

app.get('/', function(req, res) {
    var filePath = 'index.html';
    res.sendFile(filePath);
});

app.post("/send", upload.single('uploadfile'), function (req, res) {
    MongoClient.connect(url, function (err, db) {
        if (err) {
            console.log("DB connection error");
        } else {
            console.log("DB connection is successful");
            console.log(req.file);
            var insertdata  ={};
            insertdata["file"] = fs.readFileSync(req.file.path);

            var dbo = db.db("health");

            dbo.collection("send").insertOne(insertdata, function (err, result) {
                if (err) throw err;
                db.close(true);
                res.json("Successfully persisted in database");
            });
        }
    })
});

app.listen(3000);
