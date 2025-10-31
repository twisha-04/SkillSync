function Progress({ score, index, numQuestions, maxPossiblePoints, answer }) {
  return (
    <header className="progress">
      <progress
        max={numQuestions}
        value={index + Number(answer !== null)}
      ></progress>
      {console.log(Number(answer !== null))}
      <p>
        Question {index + 1}/{numQuestions}
      </p>
      <p>
        Your Score: {score}/{maxPossiblePoints}
      </p>
    </header>
  );
}

export default Progress;
