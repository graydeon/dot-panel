// SPDX-License-Identifier: AGPL-3.0-only
export type QuestionState={question:{expires:string}|null,answer:unknown|null};
export function hasPendingQuestion(state:QuestionState|null,at=Date.now()){return !!state?.question&&!state.answer&&Date.parse(state.question.expires)>at;}
export function findProject<T extends {name:string}>(projects:T[],name:string):T|undefined{const normalize=(value:string)=>value.toLowerCase().replace(/[^a-z0-9]/g,'');return projects.find(p=>normalize(p.name)===normalize(name));}
