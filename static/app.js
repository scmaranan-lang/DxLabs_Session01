const namesInput = document.querySelector("#names");
const countBadge = document.querySelector("#name-count");
const pickButton = document.querySelector("#pick-button");
const buttonLabel = document.querySelector("#button-label");
const statusMessage = document.querySelector("#status-message");
const resultCard = document.querySelector("#result");
const resultLabel = document.querySelector("#result-label");
const countdownDisplay = document.querySelector("#countdown");
const winnerDisplay = document.querySelector("#winner");
const resultCaption = document.querySelector("#result-caption");

function getNames() {
  return namesInput.value
    .split(/\r?\n/)
    .map((name) => name.trim())
    .filter(Boolean);
}

function updateNameCount() {
  const count = getNames().length;
  countBadge.textContent = `${count} ${count === 1 ? "name" : "names"}`;
  pickButton.disabled = count === 0 || count > 500;
  statusMessage.textContent = count > 500 ? "Please enter no more than 500 names." : "";
}

function wait(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

async function startPick() {
  const names = getNames();
  if (!names.length || names.length > 500) {
    updateNameCount();
    return;
  }

  pickButton.disabled = true;
  namesInput.disabled = true;
  buttonLabel.textContent = "Picking...";
  statusMessage.textContent = "";
  resultCard.hidden = false;
  resultLabel.textContent = "GETTING READY...";
  countdownDisplay.hidden = false;
  winnerDisplay.hidden = true;
  resultCaption.hidden = true;

  try {
    for (let number = 5; number > 0; number -= 1) {
      countdownDisplay.textContent = number;
      countdownDisplay.style.animation = "none";
      void countdownDisplay.offsetWidth;
      countdownDisplay.style.animation = "";
      await wait(1000);
    }

    resultLabel.textContent = "AND THE PICK IS...";
    countdownDisplay.hidden = true;
    const response = await fetch("/api/pick", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ names }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "The name could not be picked. Please try again.");
    }

    winnerDisplay.textContent = payload.name;
    winnerDisplay.hidden = false;
    resultCaption.hidden = false;
  } catch (error) {
    resultCard.hidden = true;
    statusMessage.textContent = error.message || "Something went wrong. Please try again.";
  } finally {
    namesInput.disabled = false;
    pickButton.disabled = getNames().length === 0 || getNames().length > 500;
    buttonLabel.textContent = "Pick a name";
  }
}

namesInput.addEventListener("input", updateNameCount);
pickButton.addEventListener("click", startPick);
updateNameCount();
