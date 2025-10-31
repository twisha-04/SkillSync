import { useEffect, useReducer } from "react";
import Loader from "./Loader";
import StartScreen from "./startScreen";
import Error from "./Error";
import Question from "./Question";
import Footer from "./Footer";
import Progress from "./Progress";
import FinishScreen from "./FinishScreen";

const initialState = {
  questions: [],
  // loading , active , ready , active , error , finished
  status: "ready",
  index: 0,
  answer: null,
  score: 0,
  highScore: 0,
  secondsRemaining: null,
};

function reducer(state, action) {
  switch (action.type) {
    case "dataReceived":
      // console.log(action.payload);
      return { ...state, questions: action.payload, status: "ready" };
    case "dataFailed":
      return { ...state, status: "error" };
    case "startQuiz":
      return {
        ...state,
        status: "active",
        secondsRemaining: state.questions.length * 30,
      };
    case "newAnswer":
      const question = state.questions.at(state.index);
      return {
        ...state,
        answer: action.payload,
        score:
          action.payload === question.correctOption
            ? state.score + question.points
            : state.score,
      };
    case "newQuestion":
      return { ...state, index: state.index + 1, answer: null };
    case "finish":
      return {
        ...state,
        highScore:
          state.score > state.highScore ? state.score : state.highScore,
        status: "finished",
      };
    case "restart":
      console.log(state.questions);
      return {
        ...initialState,
        questions: state.questions,
      };
    // return {
    //   ...state,
    //   ascore: 0,
    //   highScore: 0,
    //   index: 0,
    //   answer: null,
    //   status: "ready",
    // };
    case "tick":
      const next = state.secondsRemaining - 1;
      const done = next <= 0;

      return {
        ...state,
        secondsRemaining: done ? 0 : next, // clamp at 0
        status: done ? "finished" : state.status,
      };
    // return {
    //   ...state,
    //   secondsRemaining: state.secondsRemaining - 1,
    //   status: state.secondsRemaining === 0 ? "finished" : state.status,
    // };
    default:
      throw new Error("unrecognized Action");
  }
}

function Quiz() {
  const [
    { questions, status, index, answer, score, highScore, secondsRemaining },
    dispatch,
  ] = useReducer(reducer, initialState);
  const numQuestions = questions.length;
  const maxPossiblePoints = questions.reduce(
    (prev, curr) => prev + curr.points,
    0
  );
  useEffect(function () {
    fetch("http://localhost:8000/questions")
      .then((res) => res.json())
      .then((data) => dispatch({ type: "dataReceived", payload: data }))
      .catch((error) => dispatch({ type: "dataFailed" }));
  }, []);

  return (
    <main className="main">
      {" "}
      {status === "loading" && <Loader />}
      {status === "error" && <Error />}
      {status === "ready" && (
        <StartScreen numQuestions={numQuestions} dispatch={dispatch} />
      )}
      {status === "active" && (
        <>
          <Progress
            score={score}
            index={index}
            numQuestions={numQuestions}
            maxPossiblePoints={maxPossiblePoints}
            answer={answer}
          />
          <Question
            question={questions[index]}
            dispatch={dispatch}
            answer={answer}
          />
          <Footer
            dispatch={dispatch}
            answer={answer}
            index={index}
            numQuestions={numQuestions}
            secondsRemaining={secondsRemaining}
          />
        </>
      )}
      {status === "finished" && (
        <FinishScreen
          score={score}
          dispatch={dispatch}
          maxPossiblePoints={maxPossiblePoints}
          highScore={highScore}
        />
      )}
    </main>
  );
}

export default Quiz;
