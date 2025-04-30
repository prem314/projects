(* ::Package:: *)

Get[FileNameJoin[{NotebookDirectory[],"T.mx"}]]


TTransForm[expr_]:= ReleaseHold[Expand[TrigToExp[expr]] /. Exp[x_] -> Exp[HoldForm[Simplify[x, Assumptions->DrudeAssumptions]]]]


Clear[randomValue]

randomValue[expr_, exemptVars_ : {}] := Module[
  {syms, varsToReplace, vals, numValue},
  
  (* Extract all unique global symbols from the expression *)
  syms = Union[
    Cases[Hold[expr], s_Symbol /; Context[s] === "Global`", {0, Infinity}]
  ];
  
  (* Determine which symbols to replace by excluding the exempt variables *)
  varsToReplace = Complement[syms, exemptVars];
  
  (* Assign random real values between 0 and 1 to the non-exempt symbols *)
  If[Length[varsToReplace] > 0,
    vals = Thread[varsToReplace -> RandomReal[{0.1, 1}, Length[varsToReplace]]],
    vals = {}
  ];
  
  (* Print the assigned variables and their values, if any *)
  (*
  If[varsToReplace =!= {},
    Print["Assigned Values:"];
    Do[
      Print[varsToReplace[[i]], " -> ", vals[[i, 2]]],
      {i, Length[varsToReplace]}
    ];
  ];
  *)
  
  (* Compute the numerical value with replacements *)
  numValue = N[expr /. vals];
  
  (* Return the numerical value and the list of assignments *)
  {numValue, vals}
]


ValReplace = randomValue[T /. t->1][[2]]


TPlot = TTransForm[T]


TFunc[x_]:= Re[(TPlot //. ValReplace) /. t -> x]


Plot[TFunc[t],{t,1,100}]
