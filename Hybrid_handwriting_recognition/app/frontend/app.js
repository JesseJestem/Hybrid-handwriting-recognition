// const - unchangable variable, document - HTML page, getelement - take element from ID
const canvas = document.getElementById("drawingCanvas");
// take painting tool from canvas
const ctx = canvas.getContext("2d");

//every element of HTML
const labelSelect = document.getElementById("labelSelect");
const cleanBtn = document.getElementById("cleanBtn");
const saveBtn = document.getElementById("saveBtn");
const pointsCount = document.getElementById("pointsCount");
const statusText = document.getElementById("statusText");

// send data to postApi using IP of this PC (localhost)
const API_URL = "http://127.0.0.1:8000/save-sample";

// let - changable variable, mark status
let isDraving = false;
let strokes = [];
let startTime = null;

//set Select englis letters
for (let i = 65; i <= 90; i++){
    const upperLetter = String.fromCharCode(i); // transform code to letter in Unicode / ASCII
    const lowerLetter = String.fromCharCode(i + 32); // differ between upper and lower = 97(a)-65(A) = 32

    const upperOption = document.createElement("option"); // create new HTML <option></option> element
    upperOption.value = upperLetter; // <option value="A"></option>
    upperOption.textContent = upperLetter; // <option value="A">A</option>
    labelSelect.appendChild(upperOption); // add this option in labelSelect <select>

    const lowerOption = document.createElement("option");
    lowerOption.value = lowerLetter;
    upperOption.textContent = lowerLetter;
    labelSelect.appendChild(lowerOption);
}