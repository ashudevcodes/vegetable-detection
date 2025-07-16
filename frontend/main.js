const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const resultsDiv = document.getElementById("results");

navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
	video.srcObject = stream;
});

document.getElementById("capture").addEventListener("click", async () => {
	canvas.width = video.videoWidth;
	canvas.height = video.videoHeight;
	ctx.drawImage(video, 0, 0);

	canvas.toBlob(async (blob) => {
		const formData = new FormData();
		formData.append("image", blob, "frame.jpg");

		const res = await fetch("http://localhost:8080/upload", {
			method: "POST",
			body: formData,
		});

		const data = await res.json();
		showResults(data.boxes);
	}, "image/jpeg");
});

function showResults(boxes) {
	resultsDiv.innerHTML = "";
	ctx.lineWidth = 2;
	ctx.strokeStyle = "red";
	ctx.font = "16px Arial";
	ctx.fillStyle = "red";

	boxes.forEach((box) => {
		ctx.strokeRect(box.x, box.y, box.width, box.height);
		ctx.fillText(box.label, box.x, box.y - 5);

		const el = document.createElement("div");
		el.textContent = `${box.label} at (${box.x}, ${box.y})`;
		resultsDiv.appendChild(el);
	});
}

