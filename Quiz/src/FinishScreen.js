function FinishScreen({ score, maxPossiblePoints, highScore, dispatch }) {
  const percentage = (score / maxPossiblePoints) * 100;
  return (
    <>
      <div className="result">
        You scored {score} out of {maxPossiblePoints}({Math.ceil(percentage)}%)
      </div>
      <p className="highscore">(Highscore: {highScore} points)</p>
      <button
        className="btn btn-ui"
        onClick={() => dispatch({ type: "restart" })}
      >
        Restart Quiz
      </button>
    </>
  );
}

export default FinishScreen;
