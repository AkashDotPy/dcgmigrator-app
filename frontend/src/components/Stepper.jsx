import React from 'react';
import "./stepper.css";
import { TiTick } from "react-icons/ti";

const Stepper = ({ steps, currentStep, setCurrentStep }) => {
  return (
    <div className="flex flex-col items-center py-10">
      <div className="flex justify-between">
        {steps?.map((step, i) => (
          <div
            key={i}
            className={`step-item ${(currentStep === i + 1 || currentStep === 9) && "active"} ${(i + 1 < currentStep ) && "complete"}`}
            // onClick={() => setCurrentStep(i + 1)}
          >
            {/* {console.log(i + 1, currentStep)} */}
            <div className="step">
              {i + 1 < currentStep  ? <TiTick size={24} /> : i + 1}
            </div>
            <p className="text-gray-500">{step.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Stepper;
