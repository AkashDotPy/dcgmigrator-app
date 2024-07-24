import React from 'react';

const Breadcrumb = ({ steps, currentStep, setCurrentStep }) => {
  return (
    <div className="flex bg-gray-100 p-3 rounded">
      <div className="list-reset flex text-grey-dark">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center">
            {index !== 0 && <span className="mx-2">/</span>}
            <div>  </div>
            <span
              className={`${index + 1 < currentStep ? "text-sky-600 hover:underline cursor-pointer" : "text-slate-500"} 
                          ${currentStep === index + 1 ? "font-semibold text-sky-600 text-lg": ""}`}
              onClick={() => index + 1 <= currentStep && setCurrentStep(index + 1)}
            >
              {step.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Breadcrumb;
