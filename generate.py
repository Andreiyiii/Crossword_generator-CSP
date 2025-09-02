import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.

        """
        for key,values in self.domains.copy().items():
            for domain in values.copy():
                if len(domain)!=key.length:
                    values.remove(domain)

        for key,values in self.domains.copy().items():
            print(key,values)

        # for var in self.crossword.variables:
        #     print(str(var)[:6])

            #python generate.py data/structure0.txt data/words0.txt



        # for var in self.domains:
        #     self.domains[var] = {
        
        #         word for word in self.domains[var]
        #         if len(word) == var.length
        #     }

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        """
        revised=False
        overlap = self.crossword.overlaps[x,y]
        if overlap is None:
            return False
        (i,j)=overlap
        for x_word in self.domains[x].copy():
            ok=0
            for y_word in self.domains[y].copy():
                if x_word[i]== y_word[j]:
                    ok=1
            if ok==0:
                self.domains[x].remove(x_word)
                revised=True



        return revised
        raise NotImplementedError

   

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        """
        queue=[]
        if arcs is None:
            list=[]
            for x in self.crossword.variables:
                for y in self.crossword.variables:
                    if x!=y:
                        list.append((x,y))  
            queue=list
        else:
            queue=arcs
            
        while queue:
            (x,y)=queue.pop(0)
            
            if self.revise(x,y):
                
                if len(self.domains[x])==0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z,x))  
        return True
                
                
        # for i in queue:
        #     print(i)

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete return False otherwise.
        """
        ok=True
        for var in self.domains:
            if var not in assignment or assignment[var] is None:
                ok=False
        return ok

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var,domain in assignment.items():
                if len(domain) != var.length:
                    return False
        if len(set(assignment.values())) < len(assignment):
            return False
        vars = list(assignment.keys())    

        for i in range(len(vars)):
            for j in range(i+1,len(vars)):
                overlap=self.crossword.overlaps[(vars[i],vars[j])]
                if overlap is None:
                    continue
                (m,n)=overlap
                if assignment[vars[i]][m] != assignment[vars[j]][n]:
                    return False
        return True
        

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of var, sorted by
        the number of values they rule out for neighboring variables.
        The first value in the list,is the one that rules out the 
        fewest values.
        """
        list=[]
        neighbors=self.crossword.neighbors(var)
        assigned_already={variable for variable in assignment}
        neighbors=neighbors-assigned_already

        how_many_dict={value:0 for value in self.domains[var]}
        for value in self.domains[var]:
            how_many=0
            for neighbor in neighbors:
                overlap=self.crossword.overlaps[(var,neighbor)]
                if overlap !=None:
                    (i,j)=overlap
                    for neighbor_word in self.domains[neighbor]:
                        if value[i]!=neighbor_word[j]:
                            how_many+=1
            how_many_dict[value]=how_many

        sorted_dict= sorted(how_many_dict, key=lambda x:how_many_dict[x])
        list = [key for key in sorted_dict]
        return list

    def select_unassigned_variable(self, assignment):
            """
            Return an unassigned variable not already part of assignment
            with the minimum number of remaining values in its domain. 
            If there is a tie, choose the variable with the most neighbors
            """

            
            assigned_variables={var for var in assignment}
            not_assigned=self.crossword.variables-assigned_variables
            min_domain_dict={var:0 for var in not_assigned}
            for var in not_assigned:
                min_domain_dict[var]=(len(self.domains[var]),len(self.crossword.neighbors(var)))
            sorted_dict=sorted(min_domain_dict,key=lambda x:(min_domain_dict[x][0],min_domain_dict[x][1]))
            for item in sorted_dict:
                return item
    
    def backtrack(self, assignment):
        """
        Using Backtracking Search, return a complete assignment if possible to do so.
        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment)==True:
            return assignment
        
        var=self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var,assignment):
            assignment[var]=value
            if self.consistent(assignment)==True:
                result=self.backtrack(assignment)
                if result!=None:
                    return result
            del assignment[var]
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
