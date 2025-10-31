function StartScreen({ numQuestions, dispatch }) {
  return (
    <div className="start">
      <h2>Welcome to the Quiz!</h2>
      <h3>{numQuestions} Questions to test your mastery</h3>
      <button
        className="btn btn-ui"
        onClick={() => dispatch({ type: "startQuiz" })}
      >
        Let's Start
      </button>
    </div>
  );
}

export default StartScreen;
