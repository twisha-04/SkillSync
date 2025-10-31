import NextButton from "./NextButton";
import Timer from "./Timer";

function Footer({ dispatch, answer, index, numQuestions, secondsRemaining }) {
  return (
    <div>
      <Timer dispatch={dispatch} secondsRemaining={secondsRemaining} />
      <NextButton
        dispatch={dispatch}
        answer={answer}
        index={index}
        numQuestions={numQuestions}
      />
    </div>
  );
}

export default Footer;
