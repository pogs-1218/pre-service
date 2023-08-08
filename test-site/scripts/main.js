const myImage = document.querySelector("img");
let myButton = document.querySelector("button");
let myHeading = document.querySelector("h1");

if (!localStorage.getItem("name")) {
  setUserName();
} else {
  const storedName = localStorage.getItem("name");
  myHeading.textContent = `AI is the future, ${storedName}`;
}

myButton.onclick = () => {
  setUserName();
};

myImage.onclick = () => {
  const mySrc = myImage.getAttribute("src");
  if (mySrc === "images/ai.jpeg") {
    myImage.setAttribute("src", "images/ai2.jpeg");
  } else {
    myImage.setAttribute("src", "images/ai.jpeg");
  }
};

function setUserName() {
  const myName = prompt("Please enter your name.");
  if (!myName) {
    setUserName();
  }
  localStorage.setItem("name", myName);
  myHeading.textContent = `AI is the future, ${myName}`;
}
