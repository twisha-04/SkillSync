import { useEffect } from "react";

function Timer({ dispatch, secondsRemaining }) {
  const mins = Math.floor(secondsRemaining / 60);
  const seconds = secondsRemaining % 60;
  useEffect(
    function () {
      if (secondsRemaining <= 0) return;

      const id = setTimeout(function () {
        dispatch({ type: "tick" });
      }, 1000);
      return function () {
        clearTimeout(id);
      };
    },
    [secondsRemaining, dispatch]
  );
  return (
    <div className="timer">
      {mins} : {seconds}
    </div>
  );
}

export default Timer;
