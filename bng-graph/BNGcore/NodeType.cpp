/*
 * NodeType.cpp
 *
 *  Created on: June 10, 2010
 *      Author: justin
 */

#include "BNGcore.hpp"
using namespace BNGcore;


// define static members



//////////////
// NODETYPE //
//////////////

// Constructor 
NodeType::NodeType  ( const std::string & _type_name, const StateType & _state_type )
  : type_name( _type_name ),
    parent_type( 0 ),
    state_type( &_state_type )
{
    instance_flag = false;
};


// Constructor w/ parent type
NodeType::NodeType  ( const std::string & _type_name, const NodeType & _parent_type, const StateType & _state_type )
  : type_name( _type_name ),
    parent_type( &_parent_type ),
    state_type( &_state_type )
{
    instance_flag = false;
};


// get label method (concatenates local label with category index)
std::string
NodeType::get_label ( ) const
{
    std::stringstream s;
    s << type_name;
    return s.str();   
}    


// nodetype equal operator
bool
NodeType::operator== ( const NodeType & type2 ) const
{
    return ( type_name == type2.type_name );
}


// less than comparator for sorting
bool
NodeType::less ( const NodeType & type2 ) const
{
    return ( type_name < type2.type_name );
}


// partial ordering comparator (not same as sorting less than!)
//  returns true if type2 is an ancestor of this.
bool
NodeType::operator< ( const NodeType & type2 ) const
{
    if ( *this == type2 ) return true;
    
    const NodeType * parent;
    parent = this->parent_type;
    while ( parent != 0 )
    {
        if ( *parent == type2 ) return true;
        parent = parent->parent_type;
    }
    return false; 
}


// Add required in edges
bool
NodeType::add_edges_in ( NodeType & node_type, int multiplicity )
{
    type_iter = edges_in.find ( &node_type );
    if ( type_iter == edges_in.end() )
    {
        edges_in.insert (  std::pair < NodeType*, NodeFunction* >
                           ( &node_type, new ConstantNodeFunction(multiplicity) )  );
        return true;
    }
    else  return false;
};

// Add required in edges
bool
NodeType::add_edges_in ( NodeType & node_type, NodeFunction & nodefcn )
{
    type_iter = edges_in.find ( &node_type );
    if ( type_iter == edges_in.end() )
    {
        edges_in.insert (  std::pair < NodeType*, NodeFunction* >
                                                ( &node_type, nodefcn.clone() )  );
        return true;
    }
    else  return false;
};

// Add required out edges
bool
NodeType::add_edges_out ( NodeType & node_type, int multiplicity )
{
    type_iter = edges_out.find ( &node_type );
    if ( type_iter == edges_out.end() )
    {
        edges_out.insert (  std::pair < NodeType*, NodeFunction* >
                            ( &node_type, new ConstantNodeFunction(multiplicity) )  );
        return true;
    }
    else  return false;
}

// Add required out edges
bool
NodeType::add_edges_out ( NodeType & node_type, NodeFunction & nodefcn )
{
    type_iter = edges_out.find ( &node_type );
    if ( type_iter == edges_out.end() )
    {
        edges_out.insert (  std::pair < NodeType*, NodeFunction* >
                                                 ( &node_type, nodefcn.clone() )  );
        return true;
    }
    else  return false;
}

     
// write NodeType to a string            
std::string
NodeType::get_BNG2_string ( bool instance ) const
{
    std::stringstream s;
    s << get_label();

    if ( !instance )
    {
        const LabelStateType* lst = dynamic_cast<const LabelStateType*>(&get_state_type());
        if (lst) {
            const std::set<std::string>& states = lst->get_states();
            for (std::set<std::string>::const_iterator it = states.begin(); it != states.end(); ++it) {
                if (*it != "?") {
                    s << "~" << *it;
                }
            }
        }
    }
    return s.str();
}






////////////////
// ENTITYTYPE //
////////////////

EntityType::EntityType ( const std::string & type_name,
                         const NodeType & parent_type,
                         const StateType & state_type  )
    : NodeType ( type_name, parent_type, state_type )
{

}


// write EntityType to a BNG2 string            
std::string
EntityType::get_BNG2_string ( bool instance ) const
{
    std::stringstream s;
    s << NodeType::get_BNG2_string(instance);

    if ( !instance )
    {
        bool found_entity_child = false;
        std::stringstream t;

        for (typemap_const_iter_t it = edges_out_begin(); it != edges_out_end(); ++it) {
            NodeType* child_type = it->first;
            if (*child_type < ENTITY_NODE_TYPE) {
                const ConstantNodeFunction* cnf = dynamic_cast<const ConstantNodeFunction*>(it->second);
                int mult = 1;
                if (cnf) mult = cnf->get_value();

                for (int i = 0; i < mult; ++i) {
                    if (found_entity_child) t << ",";
                    t << child_type->get_BNG2_string(false);
                    found_entity_child = true;
                }
            }
        }
        if (found_entity_child) {
            s << "(" << t.str() << ")";
        }
    }

    return s.str();
} 






//////////////
// BONDTYPE //
//////////////

// constructor
BondType::BondType ( BondNodeFunction & typing_fcn )
    : NodeType ( "!", LINK_NODE_TYPE, BOND_STATE_TYPE )
{
    add_edges_in( ENTITY_NODE_TYPE, typing_fcn );
}


// write NodeType to a string            
std::string
BondType::get_BNG2_string ( bool instance ) const
{
    std::stringstream s;
    return s.str();
} 


// bond typing function
int
BondNodeFunction::map ( const Node & node ) const
{
    // argument x = targets_needed + named_targets
    if ( node.get_state() == BOUND_STATE )
        return 2;
    else
        return 1;
}

// bond typing function
int
BondNodeFunction::map ( const Node & node1, const Node & node2 ) const
{
    // argument x = targets_needed + named_targets
    if ( node1.get_state() == UNBOUND_STATE  ||  node2.get_state() == UNBOUND_STATE )
        return 1;
    else
        return 2;
}


