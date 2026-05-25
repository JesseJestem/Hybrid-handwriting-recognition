// const - unchangable variable, document - HTML page, getelement - take element from ID
const canvas = document.getElementById("drawingCanvas");
// take painting tool from canvas
const ctx = canvas.getContext("2d");

//every element of HTML
const labelSelect = document.getElementById("labelSelect");
const clearBtn = document.getElementById("clearBtn");
const saveBtn = document.getElementById("saveBtn");
const pointsCount = document.getElementById("pointsCount");
const statusText = document.getElementById("statusText");
const samplesCount = document.getElementById("samplesCount");

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
    lowerOption.textContent = lowerLetter;
    labelSelect.appendChild(lowerOption);
}

// brush setup
ctx.lineWidth = 12;
ctx.lineCap = "round";
ctx.lineJoin = "round";
ctx.strokeStyle = "black";

//white canvas
clearCanvas();

// get pointer position
function getPointerPosition(event) {
    const rect = canvas.getBoundingClientRect(); // take data from customer touch

    return {
        x: event.clientX - rect.left, //coordinate in browser window
        y: event.clientY - rect.top //coordinate in browser window
    }
}

// get customer touch pressure (mouse is ussually 0 or 0,5, real touch 0-1, take 0,5 if dont have data)
function getPressure(event) {
    return event.pressure || 0.5;
}

// add point in strokes
function addPoint(event, isPenDown) {
    if (startTime === null) {
        startTime = performance.now(); // take now time if null (first point)
    }

    const pos = getPointerPosition(event);
    const currentTime = performance.now();

    strokes.push({ //add new element in array with data
        x: pos.x,
        y: pos.y,
        t: currentTime - startTime,
        pressure: getPressure(event),
        pen_down: isPenDown //boolean paint now? - true/false
    });

    pointsCount.textContent = strokes.length;  //update point counting
}

//wait for painting
canvas.addEventListener("pointerdown", (event) => {
    isDraving = true;
    canvas.setPointerCapture(event.pointerId); //take pointer position

    const pos = getPointerPosition(event);

    ctx.beginPath(); //new painting line
    ctx.moveTo(pos.x, pos.y); //set starting point

    addPoint(event, true) //save first point position
})

//lisen to drawing
canvas.addEventListener("pointermove", (event) => {
    if(!isDraving) return; //take only drawing action, dont take just mouse moving

    const pos = getPointerPosition(event);

    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();

    addPoint(event, true);
})

//lisen when drawing is end
canvas.addEventListener("pointerup", (event) => {
    if(!isDraving) return;

    isDraving = false;
    addPoint(event, false); //add last point
})

//cancell collecting data if drawing was cancelled
canvas.addEventListener("pointercancel", () => {
    isDraving = false;
})

//clear button
clearBtn.addEventListener("click",() => {
    clearCanvas();
})

//save buttion - send data to backend
saveBtn.addEventListener("click", async() =>{ //async - await, waiting for backend operation
    if(strokes.length === 0) { //dont save if no any data
        statusText.textContent = "Nothing to save";
        return;
    }

    const label = labelSelect.value; //take label of drawed
    const image = canvas.toDataURL("image/png"); //take image of canvas to png base64

    //seng body of API data to backend in setted formate
    const payload = {
        label: label,
        image: image,
        strokes: strokes,
        canvas_width: canvas.width,
        canvas_height: canvas.height
    };

    try { //try to save data, if smth wrong - catch
        statusText.textContent = "Saving~~~";

        const response = await fetch(API_URL, { //API REQUEST POST SEND DATA! fetch - JS sender
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();  //take backend response
        
        if (!response.ok) { //if response not ok - pass to catch
            throw new Error(JSON.stringify(result));
        }

        samplesCount.textContent = result.samples_count; //return samples count
        statusText.textContent = `Saved ${result.label}, points: ${result.points_count}, samples: ${result.samples_count}`;

        clearCanvas();
    }   catch(error) {
        console.error(error);
        statusText.textContent = 'Saved failed!!!';
    }
});

//display clear after painting
function clearCanvas() {
    ctx.fillStyle = "white";
    ctx.fillRect(0,0, canvas.width, canvas.height);

    ctx.lineWidth = 12;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "black";

    strokes = [];
    startTime = null;
    pointsCount.textContent = "0";
    statusText.textContent = "Ready";
}