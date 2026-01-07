from ortools.sat.python import cp_model
from typing import List, Dict, Any, Optional

class BlockScheduler:
    """
    Generated valid block section schedules using OR-Tools CP-SAT.
    """
    def __init__(self, subjects: List[Dict], professors: List[Dict], blocks: List[Dict], time_slots: List[Dict]):
        self.subjects = subjects
        self.professors = professors
        self.blocks = blocks
        self.time_slots = time_slots
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}

    def _initialize_variables(self):
        """
        Define decision variables: x[subject_id][block_id][slot_index]
        """
        for block in self.blocks:
            b_id = block['id']
            for subject_id in block['curriculum']:
                for slot_idx in range(len(self.time_slots)):
                    self.variables[(subject_id, b_id, slot_idx)] = self.model.NewBoolVar(
                        f'assign_{subject_id}_{b_id}_{slot_idx}'
                    )

    def _add_constraints(self):
        # 1. Curriculum Requirement: Each subject per block must have the required number of slots.
        subject_map = {s['id']: s for s in self.subjects}
        for block in self.blocks:
            b_id = block['id']
            for subject_id in block['curriculum']:
                required_slots = subject_map[subject_id]['required_slots']
                self.model.Add(
                    sum(self.variables[(subject_id, b_id, slot_idx)] 
                        for slot_idx in range(len(self.time_slots))) == required_slots
                )

        # 2. No Overlaps within a Block: At most one subject per block per time slot.
        for block in self.blocks:
            b_id = block['id']
            for slot_idx in range(len(self.time_slots)):
                self.model.Add(
                    sum(self.variables[(subject_id, b_id, slot_idx)] 
                        for subject_id in block['curriculum']) <= 1
                )

        # 3. Professor Availability and Qualifications:
        # A subject can only be scheduled if at least one qualified and available professor exists.
        # For simplicity in this variation, we ensure that IF a slot is assigned, 
        # there is AT LEAST ONE professor who COULD teach it.
        for block in self.blocks:
            b_id = block['id']
            for subject_id in block['curriculum']:
                for slot_idx in range(len(self.time_slots)):
                    # Check if any professor is qualified for this subject AND available at this slot
                    qualified_profs = [
                        p for p in self.professors 
                        if subject_id in p['qualified_subjects'] and slot_idx in p['availability']
                    ]
                    if not qualified_profs:
                        # No one can teach this subject at this time
                        self.model.Add(self.variables[(subject_id, b_id, slot_idx)] == 0)

    def solve(self) -> Optional[Dict[str, Any]]:
        self._initialize_variables()
        self._add_constraints()

        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            results = {}
            for block in self.blocks:
                b_id = block['id']
                results[block['name']] = []
                for subject_id in block['curriculum']:
                    subject_name = next(s['name'] for s in self.subjects if s['id'] == subject_id)
                    assigned_slots = [
                        slot_idx for slot_idx in range(len(self.time_slots))
                        if self.solver.Value(self.variables[(subject_id, b_id, slot_idx)]) == 1
                    ]
                    for slot_idx in assigned_slots:
                        slot = self.time_slots[slot_idx]
                        results[block['name']].append({
                            'subject': subject_name,
                            'day': slot['day'],
                            'start': slot['start'],
                            'end': slot['end']
                        })
            return results
        else:
            return None
