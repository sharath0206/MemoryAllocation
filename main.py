import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tkinter as tk
from tkinter import messagebox
from matplotlib.widgets import Button

UNIT_MAP = {'KB': 1, 'MB': 1024}

def parse_block(block_str):
    size, unit = block_str.strip().split()
    
    return int(size) * UNIT_MAP[unit.upper()], unit.upper()

def parse_process(proc_str):
    size, unit = proc_str.strip().split()
    return int(size) * UNIT_MAP[unit.upper()], unit.upper()

def get_input():
    print("Enter memory blocks (e.g. '100 KB', '1 MB'), separated by comma:")
    blocks = input().split(',')
    block_list = [parse_block(b) for b in blocks]
    print("Enter process sizes (e.g. '50 KB', '512 KB', '2 MB'), separated by comma:")
    procs = input().split(',')
    proc_list = [parse_process(p) for p in procs]
    return block_list, proc_list

def convert_to_str(size):
    if size >= 1024:
        return f"{size//1024} MB"
    else:
        return f"{size} KB"

# Allocation strategies

def first_fit(blocks, procs):
    allocation = [-1]*len(procs)
    block_status = blocks[:]
    frag_internal = [0]*len(procs)
    for i, (psize, _) in enumerate(procs):
        for j, (bsize, _) in enumerate(block_status):
            if bsize >= psize:
                allocation[i] = j
                frag_internal[i] = bsize - psize
                block_status[j] = (bsize - psize, 'KB')
                break
    return allocation, frag_internal, block_status

def best_fit(blocks, procs):
    allocation = [-1]*len(procs)
    block_status = blocks[:]
    frag_internal = [0]*len(procs)
    for i, (psize, _) in enumerate(procs):
        best_idx = -1
        min_diff = float('inf')
        for j, (bsize, _) in enumerate(block_status):
            if bsize >= psize and (bsize - psize) < min_diff:
                min_diff = bsize - psize
                best_idx = j
        if best_idx != -1:
            allocation[i] = best_idx
            frag_internal[i] = block_status[best_idx][0] - psize
            block_status[best_idx] = (block_status[best_idx][0] - psize, 'KB')
    return allocation, frag_internal, block_status

def worst_fit(blocks, procs):
    allocation = [-1]*len(procs)
    block_status = blocks[:]
    frag_internal = [0]*len(procs)
    for i, (psize, _) in enumerate(procs):
        worst_idx = -1
        max_diff = -1
        for j, (bsize, _) in enumerate(block_status):
            if bsize >= psize and (bsize - psize) > max_diff:
                max_diff = bsize - psize
                worst_idx = j
        if worst_idx != -1:
            allocation[i] = worst_idx
            frag_internal[i] = block_status[worst_idx][0] - psize
            block_status[worst_idx] = (block_status[worst_idx][0] - psize, 'KB')
    return allocation, frag_internal, block_status

def visualize(blocks, procs, allocation, frag_internal, strategy_name):
    fig, ax = plt.subplots(figsize=(12, 3))  # Increased figure size
    plt.subplots_adjust(bottom=0.2)
    y = 0.5
    colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#FF5722', '#00BCD4', '#E91E63', '#8BC34A']
    process_colors = {i: colors[i % len(colors)] for i in range(len(procs))}
    total_mem = sum([b[0] for b in blocks])
    step = [0]  # Mutable container for step index

    def draw_step():
        ax.clear()
        x = 0
        for i, (bsize, _) in enumerate(blocks):
            # Draw base memory block
            rect = mpatches.Rectangle((x, y), bsize, 0.5, facecolor='lightgray', edgecolor='black')
            ax.add_patch(rect)
            
            # Add block number below
            ax.text(x + bsize/2, y - 0.1, f'Block {i+1}', ha='center', va='top')
            
            for j in range(step[0] + 1):
                if allocation[j] == i:
                    psize, _ = procs[j]
                    frag = frag_internal[j]
                    
                    # Draw allocated process
                    rect_alloc = mpatches.Rectangle((x, y), psize, 0.5,
                                                    facecolor=process_colors[j],
                                                    edgecolor='black')
                    ax.add_patch(rect_alloc)
                    
                    # Add process number in the middle of allocated block
                    ax.text(x + psize/2, y + 0.25, f'P{j+1}', 
                           ha='center', va='center', 
                           color='black', fontweight='bold')
                    
                    # Draw and label fragmentation
                    if frag > 0:
                        rect_frag = mpatches.Rectangle((x+psize, y), frag, 0.5,
                                                       facecolor='red', edgecolor='black')
                        ax.add_patch(rect_frag)
                        ax.text(x + psize + frag/2, y + 0.25, 'Frag',
                               ha='center', va='center',
                               color='white', fontsize=8)
            x += bsize
        ax.set_xlim(0, total_mem)
        ax.set_ylim(0, 2)
        ax.set_title(f"{strategy_name} - Step {step[0]+1}")
        ax.axis('off')
        legend_patches = [mpatches.Patch(color=process_colors[i], label=f'Process {i+1}') for i in range(len(procs))]
        legend_patches.append(mpatches.Patch(color='red', label='Fragmentation'))
        legend_patches.append(mpatches.Patch(color='lightgray', label='Free Memory'))
        ax.legend(handles=legend_patches, loc='upper right')
        fig.canvas.draw_idle()

    def next_step(event):
        if step[0] < len(procs) - 1:
            step[0] += 1
            draw_step()
        else:
            plt.close(fig)

    draw_step()
    ax_next = plt.axes([0.45, 0.05, 0.1, 0.075])
    btn_next = Button(ax_next, 'Next')
    btn_next.on_clicked(next_step)
    plt.show()

def fragmentation_stats(blocks, procs, allocation, frag_internal):
    total_internal = sum(frag_internal)
    external = 0
    allocated_blocks = set([a for a in allocation if a != -1])
    for i, (bsize, _) in enumerate(blocks):
        if i not in allocated_blocks:
            external += bsize
    return total_internal, external

def main():
    print("Memory Allocation Simulator (First Fit, Best Fit, Worst Fit)")
    blocks, procs = get_input()
    blocks_kb = [(size, 'KB') for size, unit in blocks]
    procs_kb = [(size, 'KB') for size, unit in procs]
    
    strategies = [('First Fit', first_fit), ('Best Fit', best_fit), ('Worst Fit', worst_fit)]
    for name, func in strategies:
        print(f"\n--- {name} ---")
        allocation, frag_internal, block_status = func(blocks_kb, procs_kb)
        visualize(blocks_kb, procs_kb, allocation, frag_internal, name)
        
        print("Allocation Results:")
        for i, alloc in enumerate(allocation):
            if alloc != -1:
                print(f"Process {i+1} ({convert_to_str(procs_kb[i][0])}) -> Block {alloc+1} "
                      f"({convert_to_str(blocks_kb[alloc][0])}), Internal Fragmentation: {frag_internal[i]} KB")
            else:
                print(f"Process {i+1} ({convert_to_str(procs_kb[i][0])}) -> Not Allocated")
        
        leftover = [b[0] for b in block_status]
        print("Leftover Memory in Blocks:", ', '.join([convert_to_str(l) for l in leftover]))
        total_internal, external = fragmentation_stats(blocks_kb, procs_kb, allocation, frag_internal)
        print(f"Total Internal Fragmentation: {total_internal} KB")
        print(f"Total External Fragmentation: {external} KB")

if __name__ == "__main__":
    main()
